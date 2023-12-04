import os
# conda activate openai
import openai
openai.organization = "org-90F4mEMVKKl9NEm21GQVVFCb"
# set API key in Terminal: export OPENAI_API_KEY=xxx
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.Model.list()

# The raw text file can be obtained using Mathematica
# text = Import["filename.pdf", "Plaintext"]
# Export["filename.txt",text]

input_file = '/Users/charlesdu/Documents/research/paper_of_interest/remeshing_pipeline/CAD22_mesh_cutting_for_atlas_packing.txt'
output_file = '/Users/charlesdu/Documents/research/paper_of_interest/remeshing_pipeline/CAD22_mesh_cutting_for_atlas_packing(clean).txt'
max_chars = 2000
model_name = "gpt-4"
# "gpt-3.5-turbo"

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

# Initialize an empty string to store the cleaned text
cleaned_text = ""

# Process each chunk with GPT
for i, chunk in enumerate(chunks):
	print('=========================================')
	print(f"chunk {i+1}/{len(chunks)}")
	print('-----------------------------------------')
	print(chunk)
	print('-----------------------------------------')
	response = openai.ChatCompletion.create(
  		model=model_name,
  		messages=[
        		{"role": "user", "content": f"Please remove all non-essential parts, such as page numbers, line numbers, references, acknowledgments, and contact information, from the following text segment converted from a PDF of an research paper (Please only return the cleaned-up text, no rephrase, no explanation): \n{chunk}"},
    		]
	)
	cleaned_chunk = response['choices'][0]['message']['content']
	print(cleaned_chunk)
	print('=========================================')
	cleaned_text += cleaned_chunk.strip()

# Save cleaned_text to an output file
with open(output_file, "w") as f:
    f.write(cleaned_text)

