import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_gpt(event_list, deterministic=False):
    """
    Queries GPT-3.5 to generate a response based on the given event list.
    
    @param event_list: The list of events to be used as input.
    @param deterministic: Flag indicating whether to use deterministic mode for GPT response generation.
    
    @return: The response generated by GPT-3.5 as a list of strings.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "system",
                "content": "Creative assistant in generating sound prompts from a given list of events. Outputs a json object of sounds. Size of the output should be the same as the input"
            },
            {
                "role": "user",
                "content": "[\"Commute to work\", \"Walk by the beach\"]"
            },
            {
                "role": "assistant",
                "content": "{sounds: [\"Cars honking in traffic\", \"Footsteps tapping on the sand with waves in the background\"]}"
            },
            {
                "role": "user",
                "content": "[\"Virtual Meeting with Nathan\", \"Beer and Chips with Friends\"]"
            },
            {
                "role": "assistant",
                "content": "{sounds: [\"Keyboard typing and mouse clicks\", \"Laughter and the clinking of glasses, crunching of chips\"]}"
            },
            {
                "role": "user",
                "content": "[\"Meeting with Joe\"]"
            },
            {
                "role": "assistant",
                "content": "{sounds: [\"Keyboard typing and mouse clicks with chatter in the background\"]}"
            },
            {
                "role": "user",
                "content": "[\"'23.FAL.B.1 Pod Meeting - MLH Fellowship\", \"Oscar Mier and Nathan Kurelo Wilk\", \"Monday MS FinTech Classes\", \"Tuesday MS FinTech Classes\", \"23.FAL.B.1 Pod Meeting - MLH Fellowship\", \"Wednesday MS FinTech Classes\"]"
            },
            {
                "role": "assistant",
                "content": "{sounds: [\"Mic feedback, low murmur of voices discussing on a conference call\",\"Ambient room noise\",\"Turning pages, lecturer speaking faintly in the background\",\"Turning pages, lecturer speaking faintly in the background\",\"Mic feedback, low murmur of voices discussing on a conference call\",\"Turning pages, lecturer speaking faintly in the background\"]}"
            },
            {
                "role": "user",
                "content": json.dumps(event_list)
            }
        ],
        temperature=0 if deterministic else 1,
        max_tokens=1101,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={ "type": "json_object" }
    )
    response = json.loads(response.choices[0].message.content).get("sounds")
    print("GPT Response", response)
    return response