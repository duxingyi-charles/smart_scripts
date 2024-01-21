import argparse
# conda activate openai
from openai import OpenAI

# The raw text file can be obtained using Mathematica
# text = Import["filename.pdf", "Plaintext"]
# Export["filename.txt",text]

def main():
    parser = argparse.ArgumentParser(description="Generate doxygen documentation for C++ header.")
    parser.add_argument('in_path',
                        metavar='path',
                        type=str,
                        help='input file path')
    # optional argument: output path
    parser.add_argument('-o',
                        '--out_path',
                        type=str,
                        help='output path')
    args = parser.parse_args()

    input_file = args.in_path
    output_file = args.out_path
    if output_file is None:
        input_splits = input_file.split('.')
        extension = input_splits[-1]
        name = ".".join(input_splits[:-1])
        output_file = name + "(clean)." + extension
    print("output_file: " + output_file)
    max_chars = 2000

    # Read the text file into a list of lines
    with open(input_file, "r") as f:
        lines = f.readlines()

    # Group lines to a list of bounded-length chunks
    chunks = []
    lo = 0
    hi = 0
    while hi < len(lines):
        char_count = len(lines[hi])
        while char_count < max_chars:
            hi += 1
            if hi == len(lines):
                break
            char_count += len(lines[hi])
        chunk = ''.join(lines[lo:hi])
        chunks.append(chunk)
        lo = hi

    # OpenAI
    client = OpenAI()

    # Initialize an empty string to store the cleaned text
    cleaned_text = []

    # Process each chunk with GPT
    for i, chunk in enumerate(chunks):
        print('=========================================')
        print(f"chunk {i+1}/{len(chunks)}")
        print('-----------------------------------------')
        print(chunk)
        print('-----------------------------------------')

        chat_history = [
            {
                "role": "system",
                "content": 
                """As a useful agent, your task is to clean the raw text segment converted from a PDF of an research paper and return the cleaned text to the user:
                1. remove all non-essential parts, such as page numbers, line numbers, references, acknowledgments, and contact information.
                2. remove unnecessary line breaks.
                3. correct typos.
                4. only return the cleaned-up text, no rephrase, no explanation.
                """
            },
            {
                "role": "user",
                "content": f"clean the following text: \n{chunk}"
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
        cleaned_chunk = response.choices[0].message.content
        print(cleaned_chunk)
        print('=========================================')
        cleaned_text.append(cleaned_chunk.strip())

    # Save cleaned_text to an output file
    cleaned_text = " ".join(cleaned_text)
    with open(output_file, "w") as f:
        f.write(cleaned_text)


if __name__ == '__main__':
    main()
