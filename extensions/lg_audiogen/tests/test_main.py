import os
import subprocess


def test_text_to_smallmusicgen():
    """
    Test the music generation from text with the musicgen-small model

    It requires the lg_audiogen command to be installed
    """
    # Run the lg_audiogen -m musicgen-small -d 3 -o test_audio.wav "A happy song"
    print(subprocess.run(
        ["lg_audiogen", "-m", "musicgen-small", "-d", "3", "-o", "test_audio", "A happy song"],
        capture_output=True, text=True))
    # Assert file exists and size
    print(subprocess.run(["ls"], capture_output=True, text=True))
    print(subprocess.run(["pwd"], capture_output=True, text=True))
    print(subprocess.run(["ls", ".."], capture_output=True, text=True))
    print(subprocess.run(["ls", "../.."], capture_output=True, text=True))
    assert os.path.exists("outputs/test_audio0.wav"), "The file test_audio0.wav does not exist"
    assert os.path.getsize("outputs/test_audio0.wav") > 0, "The file test_audio0.wav is empty"
    # Remove the file
    os.remove("outputs/test_audio0.wav")
    os.rmdir("outputs")


def test_single_description():
    '''
        Tests output with a single description
    '''
    # Run the script with an example description
    subprocess.run(["lg_audiogen", "dog barking"],
                    capture_output=True, text=True, check=False)
    # Assert that the output file was created
    assert os.path.exists("outputs/dog_barking0.wav"), "Output file dog_barking0.wav was not created"
    os.remove("outputs/dog_barking0.wav")


# def test_activity_to_sound():
#     '''
#         Tests output with a single activity
#     '''
#     # Run the script with an example activity
#     subprocess.run(["lg_audiogen", "-a", "meeting with nathan"],
#                     capture_output=True, text=True, check=False)
#     # print the ls command output
#     print(subprocess.run(["ls"], capture_output=True, text=True, check=False))
#     # Assert that the output file was created
#     assert os.path.exists("meeting_with_nathan0.wav"), "Output file meeting_with_nathan0.wav was not created"
#     os.remove("meeting_with_nathan0.wav")
