import argparse
from openai import OpenAI
import re
import json


def clean_code_content(code_content):
    """
    Cleans the C++ code content by removing unnecessary spaces, consecutive newlines, etc.

    :param code_content: String containing the entire code content.
    :return: Cleaned code content.
    """
    print("length (before clean): ", len(code_content))
    # Remove excess white spaces within lines
    code_content = re.sub(r'[ \t]+', ' ', code_content)

    # Remove unnecessary spaces before and after braces
    code_content = re.sub(r'\s*{\s*', ' { ', code_content)
    code_content = re.sub(r'\s*}\s*', ' } ', code_content)

    # Normalize newlines (remove consecutive newlines)
    code_content = re.sub(r'\n\s*\n', '\n', code_content)

    # Trim leading and trailing spaces on each line
    code_content = '\n'.join(line.strip() for line in code_content.split('\n'))

    print("length (after clean): ", len(code_content))

    return code_content

# def clean_code_content(code_content):
#     """
#     Cleans the C++ code content by removing unnecessary spaces and consecutive newlines,
#     while preserving indentation.

#     :param code_content: String containing the entire code content.
#     :return: Cleaned code content.
#     """
#     # Remove excess white spaces within lines, preserving indentation
#     cleaned_lines = []
#     for line in code_content.split('\n'):
#         # Find the first non-whitespace character
#         first_non_space = len(line) - len(line.lstrip())
#         # Preserve leading spaces (indentation) and remove additional spaces in the rest of the line
#         cleaned_line = line[:first_non_space] + re.sub(r'[ \t]+', ' ', line[first_non_space:])
#         cleaned_lines.append(cleaned_line)

#     cleaned_code = '\n'.join(cleaned_lines)

#     # Remove unnecessary spaces before and after braces, preserving indentation
#     cleaned_code = re.sub(r'(\S)\s*{\s*', r'\1 { ', cleaned_code)
#     cleaned_code = re.sub(r'\s*}\s*(\S)', r' } \1', cleaned_code)

#     # Normalize newlines (remove consecutive newlines)
#     cleaned_code = re.sub(r'\n\s*\n', '\n', cleaned_code)

#     # compare length of code_content and cleaned_code
#     print("length (before clean): ", len(code_content))
#     print("length (after clean): ", len(cleaned_code))

#     return cleaned_code


def split_cpp_file(file_content, max_length):
    """
    Splits the C++ file into chunks without breaking functions.
    """
    chunks = []
    current_chunk = []
    current_length = 0

    for line in file_content.split('\n'):
        line_length = len(line) + 1  # +1 for the newline character
        if current_length + line_length > max_length or '}' in line:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(line)
        current_length += line_length

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

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
    max_iter = 5
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


# def process_cpp_file(input_file_path, output_file_path, max_chunk_length):
#     """
#     Process a C++ file, adding Doxygen comments to it.
#     """
#     with open(input_file_path, 'r') as file:
#         cpp_code = file.read()

#     cpp_code = clean_code_content(cpp_code)
#     chunks = split_cpp_file(cpp_code, max_chunk_length)
#     write_chunks_to_file(chunks, output_file_path)
#     # processed_chunks = [add_doxygen_to_chunk(chunk) for chunk in chunks]

#     # with open(output_file_path, 'w') as file:
#     #     file.write('\n'.join(processed_chunks))

def process_cpp_file(input_file_path, output_file_path, max_chunk_length):
    """
    Process a C++ file, adding Doxygen comments to it.
    """
    with open(input_file_path, 'r') as file:
        cpp_code = file.read()

    cpp_code = clean_code_content(cpp_code)
    doc_code = add_doxygen_multi(cpp_code)
    if doc_code:
        with open(output_file_path, 'w') as file:
            file.write(doc_code)

def write_chunks_to_file(chunks, output_file_path, separator='--- CHUNK SEPARATOR ---\n'):
    """
    Writes the chunks to a file, adding a separator between each chunk.
    
    :param chunks: List of string chunks.
    :param output_file_path: Path to the output file.
    :param separator: String to use as a separator between chunks.
    """
    with open(output_file_path, 'w') as file:
        for i, chunk in enumerate(chunks):
            if i > 0:
                file.write(separator)
            file.write(chunk)

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="Generate doxygen documentation for c++ header.")

    # Add the arguments
    parser.add_argument('FilePath',
                        metavar='path',
                        type=str,
                        help='the path to the file')

    # Execute the parse_args() method
    args = parser.parse_args()

    input_cpp_file = args.FilePath
    output_cpp_file = input_cpp_file.replace(".h", "_doxygen.h")
    max_chunk_length = 2048  # Adjust based on GPT-4's context length limits

    process_cpp_file(input_cpp_file, output_cpp_file, max_chunk_length)


if __name__ == "__main__":
    main()




