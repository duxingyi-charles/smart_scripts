import re

def clean_code(code_content):
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

def count_object(code_chunk):
    """
    Count the number of objects (classes, functions, variables) that need to be documented in the code chunk.
    :param code_chunk: String containing the code chunk.
    :return: A dictionary containing the number of objects of each type.
    """
    pass
    
def split_code(code_content, token_limit=4095):
    """
    Split the code into chunks such that each chunk is more managable by GPTs.
    :param code_content: String containing the entire code content.
    :param token_limit: Maximum number of output tokens allowed by GPTs.
    :return: A list of code chunks.
    """
    pass