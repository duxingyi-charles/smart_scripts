import argparse
from openai import OpenAI
from analyze_cpp import *

import json
import os
import shutil

def add_doxygen_json(code_content):
    """
    Sends code content to GPT API to add Doxygen documentation.
    The response is in JSON format.
    """
    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    # model='gpt-3.5-turbo-1106',
    response_format={ "type": "json_object" },
    messages=[
        {
        "role": "system",
        "content": "You are a C++ programmer and good at writing doxygen documentation for C++ headers. \
        The user will provide the content of a C++ header file, and you will return the code with doxygen documentation added. \
        You are designed to output JSON with the following two fields: \
        - code: The code with doxygen documentation added. \
        - finished: True if you successfully finished the task, False if the output is not complete."
        },
        {
        "role": "user",
        "content": f"Add Doxygen documentation to the following C++ code: \n{code_content}"
        }
    ],
    temperature=1,
    max_tokens=4095,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    if response.choices[0].finish_reason == 'stop':
        output = response.choices[0].message.content
        json_output = json.loads(output)
        if json_output['finished']:
            return json_output['code']   

def add_doxygen(code_content):
    """
    Sends code content to GPT API to add Doxygen documentation.
    """
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        # model='gpt-3.5-turbo-1106',
        messages=[
            {
                "role": "system",
                "content": "You are a C++ programmer and good at writing doxygen documentation for C++ headers. \
                The user will provide the content of a C++ header file, and you will return the code with doxygen documentation added. \
                You should only include the documented code in your response, without any explanation. \
                If you cannot finish the task in one response, you should return the code with doxygen documentation added so far \
                and add '//to be continued' as the last line of your response."
            },
            {
                "role": "user",
                "content": f"Add Doxygen documentation to the following C++ code: \n{code_content}"
            }
        ],
        temperature=1,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # if finish_reason is not 'stop', report error and exit
    if response.choices[0].finish_reason != 'stop':
        print("Error: GPT failed to finish the task.")
        return

    output = response.choices[0].message.content
    # Remove '```cpp' and '```' from the output
    output = output.replace('```cpp', '')
    output = output.replace('```', '')

    return output

def add_doxygen_multi(code_content):
    """
    Sends code content to GPT API to add Doxygen documentation.
    Multiple requests are sent if the response is too long for one request.
    """
    client = OpenAI()

    chat_history = [
            {
                "role": "system",
                "content": "You are a C++ programmer and good at writing doxygen documentation for C++ headers. \
                The user will provide the content of a C++ header file, and you will return the code with doxygen documentation added. \
                You should only include the documented code in your response, without any explanation. \
                If you cannot finish the task in one response, you should return the code with doxygen documentation added so far \
                and add '//continue' as the last line of your response."
            },
            {
                "role": "user",
                "content": f"Add Doxygen documentation to the following C++ code: \n{code_content}"
            }
        ]

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        # model='gpt-3.5-turbo-1106',
        messages=chat_history,
        temperature=1,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # if finish_reason is not 'stop', report error and exit
    if response.choices[0].finish_reason != 'stop':
        print("Error: GPT failed to finish the task.")
        return
    response_list = [response.choices[0].message.content]
    chat_history.append(response.choices[0].message)

    # While '//continue' is in the current response, continue to send requests
    iter = 0
    max_iter = 10
    while '//continue' in response_list[-1] and iter < max_iter:
        print("iter: ", iter)
        iter += 1
        chat_history.append({
            "role": "user",
            "content": "Please continue adding doxygen documentation from the previous response. \
            Please only include the documented code in your response, without any explanation. \
            If you cannot finish the task in one response, you should return the code with doxygen documentation added so far \
            and add '//continue' as the last line of your response."
        })
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            # model='gpt-3.5-turbo-1106',
            messages=chat_history,
            temperature=1,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        if response.choices[0].finish_reason != 'stop':
            print("Error: GPT failed to finish the task.")
            return
        response_list.append(response.choices[0].message.content)
        chat_history.append(response.choices[0].message)

    # Merge all responses into one
    output = '\n'.join(response_list)
    # Remove '```cpp' and '```' from the output
    output = output.replace('```cpp', '')
    output = output.replace('```', '')
    # Remove '//to be continued' from the output
    output = output.replace('//continue', '')

    return output


def process_cpp_file(input_file_path, output_file_path):
    """
    Process a C++ file, adding Doxygen comments to it.
    """
    print(input_file_path)
    with open(input_file_path, 'r') as file:
        cpp_code = file.read()

    # cpp_code = clean_code(cpp_code)
    doc_code = add_doxygen_multi(cpp_code)
    if doc_code:
        with open(output_file_path, 'w') as file:
            file.write(doc_code)

def process_source_dir(input_dir_path, output_dir_path):
    """
    Recursively process all C++ header files in a directory, adding Doxygen comments to them.
    Save the processed files to the output directory (preserving the directory structure).
    """
    for root, dirs, files in os.walk(input_dir_path):
        # Determine the path in the output directory
        output_root = os.path.join(output_dir_path, os.path.relpath(root, input_dir_path))

        # Ensure the output directory exists
        if not os.path.exists(output_root):
            os.makedirs(output_root)

        for file in files:
            if file.endswith('.h'):  # Process C++ header files
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(output_root, file)
                if not os.path.exists(output_file_path):
                    process_cpp_file(input_file_path, output_file_path)
            else:
                # Copy other files to the output directory
                shutil.copy(os.path.join(root, file), output_root)
    

def main():
    parser = argparse.ArgumentParser(description="Generate doxygen documentation for C++ header.")
    parser.add_argument('in_path',
                        metavar='path',
                        type=str,
                        help='input path')
    # optional argument: output path
    parser.add_argument('-o',
                        '--out_path',
                        type=str,
                        help='output path')
    args = parser.parse_args()

    if os.path.isdir(args.in_path):
        # Process all C++ header files in the directory
        input_dir_path = args.in_path
        output_dir_path = args.out_path if args.out_path else input_dir_path + "_doxygen"
        process_source_dir(input_dir_path, output_dir_path)
    elif os.path.isfile(args.in_path):
        # Process a single C++ header file
        input_cpp_file = args.in_path
        if not input_cpp_file.endswith('.h'):
            print("Error: input file is not a C++ header file.")
            return
        output_cpp_file = args.out_path if args.out_path else input_cpp_file.replace(".h", "_doxygen.h")
        process_cpp_file(input_cpp_file, output_cpp_file)
    else:
        print("Error: input path is neither a file nor a directory.")


if __name__ == "__main__":
    main()
