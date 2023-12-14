import click
import datetime
from lg_audiogen.calendar_reader import calendar_to_dictionary, get_events_between_dates
from lg_audiogen.gpt_utility import query_gpt
from lg_audiogen.keyword_generator import get_prompts

# All models supported by the lg_audiogen command
SUPPORTED_MODELS = [
    "audiogen-medium",
    "musicgen-small",
    "musicgen-medium",
    "musicgen-melody",
    "musicgen-large"
]

# Musicgen models supported by the lg_audiogen command
MUSICGEN_MODELS = [
    "musicgen-small",
    "musicgen-medium",
    "musicgen-melody",
    "musicgen-large"
]

# Audiogen models supported by the lg_audiogen command
AUDIOGEN_MODELS = [
    "audiogen-medium"
]

DEFAULT_AUDIOGEN_MODEL = 'audiogen-medium'
DEFAULT_MUSICGEN_MODEL = 'musicgen-medium'
DEFAULT_AUDIO_DURATION = 5
DEFAULT_DATE = datetime.datetime.now().strftime('%Y-%m-%d')

@click.command()
@click.version_option()
@click.argument('description', nargs=-1, required=False)
@click.option('--duration', '-d', type=int, help='Duration of the generated audio.')
@click.option('--model', '-m', type=click.Choice(SUPPORTED_MODELS), help='Name of the Audiocraft AudioGen model to use.')
@click.option('--output', '-o', help='Name of the output file.')
@click.option('--batch', '-b', type=click.Path(), help='File name for batch audio description.')
@click.option('--activities', '-a', help='Comma separated string or .ics file containing activities.')
@click.option('--gpt', is_flag=True, help='Enable GPT model for activities.')
@click.option('--deterministic', is_flag=True, help='Enable deterministic generation.')
@click.option('--dates', '-dt', default=DEFAULT_DATE, help='Date in the format \'YYYY-MM-DD\' or as a range: \'YYYY-MM-DD,YYYY-MM-DD\'.')
def parse_arguments(description, duration, model, output, batch, activities, gpt, deterministic, dates):
    """
    Generates audio from description using Audiocraft's AudioGen.
    """
    both_generations = False
    if not duration:
        click.secho("No duration provided. Using default duration of 5 seconds.", fg='yellow')
        duration = DEFAULT_AUDIO_DURATION
    if duration < 1:
        raise click.BadParameter(click.style("Duration must be greater than 0.", fg='red'))
    if activities:
        descriptions, output = handle_activities(activities, gpt, deterministic, dates)
        both_generations = True
    elif batch:
        try:
            with open(batch, mode='r', encoding='utf-8') as f:
                descriptions = [line.strip() for line in f.readlines()]
        except FileNotFoundError as file_error:
            raise click.FileError(filename=batch, hint=click.style(file_error, fg='bright_red'))
    else:
        if not description:
            raise click.BadParameter(
                click.style("Description argument is required when not using --batch.", fg='bright_red'))
        descriptions = [' '.join(description)]
    if not model and not both_generations:
        click.secho("No model provided. Using default model (audiogen-medium).", fg='yellow')
        model = DEFAULT_AUDIOGEN_MODEL
    if both_generations:
        run_music_generation(descriptions, duration, DEFAULT_MUSICGEN_MODEL, output)
        run_audio_generation(descriptions, duration, DEFAULT_AUDIOGEN_MODEL, output)
    elif model in MUSICGEN_MODELS:
        run_music_generation(descriptions, duration, model, output)
    elif model in AUDIOGEN_MODELS:
        run_audio_generation(descriptions, duration, model, output)


def check_dates_format(dates):
    """
    Checks if the dates are in the correct format.
    
    @param dates: The dates to be checked. If a string is provided, it will be split by commas.
    
    @return: A list of dates.
    """
    dates = dates.split(',')
    if len(dates) > 2:
        raise click.BadParameter("Dates must be in the format \'YYYY-MM-DD\' or as a range: \'YYYY-MM-DD,YYYY-MM-DD\'.")
    for date in dates:
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise click.BadParameter("Dates must be in the format \'YYYY-MM-DD\' or as a range: \'YYYY-MM-DD,YYYY-MM-DD\'.")
    return dates

def handle_activities(activities, gpt, deterministic, dates):
    """
    Handles the activities based on the given parameters.

    @param activities: The activities to be handled. If a string is provided, it will be split by commas.
    @param gpt: Flag indicating whether to use GPT for generating response.
    @param deterministic: Flag indicating whether to use deterministic mode for GPT response generation.
    @param dates: The dates to filter the activities. If a string is provided, it should be in the format 'YYYY-MM-DD'.

    @return: A tuple containing the response generated and the list of activities.
    """
    if activities.endswith('.ics'):
        dates = check_dates_format(dates)
        calendar_events = calendar_to_dictionary(activities)
        # -1 trick to get the last element of the list (end date or single date)
        sorted_events = get_events_between_dates(calendar_events, dates[0], dates[-1])
        # build a list of event name strings if event has a name
        activities = []
        for each_date in sorted_events:
            for each_event in sorted_events[each_date]:
                if each_event['name']:
                    activities.append(each_event['name'])
    else:
        activities = activities.split(',')
    if gpt:
        response = query_gpt(activities, deterministic)
    else:
        response = get_prompts(activities, deterministic)
    activities = [activity.replace(' ', '_') for activity in activities]
    return response, activities

def run_audio_generation(descriptions, duration, model_name, output):
    """
    Load Audiocraft's AudioGen model and generate audio from the description.

    @param descriptions: The parsed arguments.
    @param duration: Duration of the generated audio.
    @param model_name: Name of the Audiocraft AudioGen model to use.
    @param output: Name of the output file.
    """
    click.secho("\nStarting the audio generation from the given descriptions", fg="bright_blue")

    # Import AudioGen, audio_write in this function to avoid time consuming imports
    from audiocraft.data.audio import audio_write
    from audiocraft.models import AudioGen

    # Load Audiocraft's AudioGen model and set generation params.
    model = AudioGen.get_pretrained(f"facebook/{model_name}")
    model.set_generation_params(duration=duration)

    try:
        # Generate audio from the descriptions
        wav = model.generate(descriptions, progress=True)
        # Save the audio on the outputs folder with the corresponding filename
        for idx, one_wav in enumerate(wav):
            # Validate the output filename
            if not output:
                filename=descriptions[idx].replace(' ', '_')
            elif type(output) == list and len(output) == len(descriptions):
                filename=output[idx].replace(' ', '_')
            else:
                filename=f"{output.replace(' ', '_')}_{idx}"

            # Will save under ouputs/{filename}.wav, with loudness normalization at -14 db LUFS.
            audio_write(f"outputs/{filename}", one_wav.cpu(), model.sample_rate,
                        strategy="loudness", loudness_compressor=True)
            click.secho(
                f"Audio generated and saved on the outputs/{filename}.wav file",
                bg="green", fg="black"
            )
    except Exception as audio_error:
        click.secho(f"Error generating audio: {audio_error}", bg="red", fg="white")


def run_music_generation(descriptions, duration, model_name, output):
    """
    Generate music from the given descritptions and save it on the outputs folder

    @param descriptions: list of descriptions to generate music from
    @param duration: duration of the audio to generate
    @param model_name: name of the musicgen model to use
    @param output: name of the output file
    """
    click.secho("\nStarting the music generation from the given descriptions", fg="bright_blue")

    # Import MusicGen, audio_write in this function to avoid time consuming imports
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write

    # Load the corresponding MusicGen model and set the generation parameters
    model = MusicGen.get_pretrained(f"facebook/{model_name}")
    model.set_generation_params(duration=duration)

    try:
        # Generate the music from the descriptions
        wav = model.generate(descriptions, progress=True)
        # Save the music on the outputs folder with the corresponding filename
        for idx, one_wav in enumerate(wav):
            # Validate the output filename
            if not output:
                filename=descriptions[idx].replace(' ', '_')
            elif type(output) == list and len(output) == len(descriptions):
                filename=output[idx].replace(' ', '_')
            else:
                filename=f"{output.replace(' ', '_')}_{idx}"

            audio_write(f"outputs/{filename}", one_wav.cpu(), model.sample_rate,
                        strategy="loudness", loudness_compressor=True)
            click.secho(
                f"Audio generated and saved on the outputs/{filename}.wav file",
                bg="green", fg="black"
            )

    except Exception as music_error:
        click.secho(f"Error generating music: {music_error}", bg="red", fg="white")
