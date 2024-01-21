import PyPDF2
import argparse


def showPdfText(filename):
    # Open the PDF file
    with open(filename, 'rb') as file:
        # Create PDF reader object
        reader = PyPDF2.PdfReader(file)
        
        # Number of pages in the PDF
        num_pages = len(reader.pages)

        # Loop through each page and extract text
        for page_num in range(num_pages):
            # Get a page
            page = reader.pages[page_num]

            # Extract text from the page
            text = page.extract_text()

            # Print the page's text
            print(f"Page {page_num + 1}:")
            print(text)
            print("-" * 50)

def extractPdfText(filename, outfile):
    full_text = ""
    with open(filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page_texts = [page.extract_text() for page in reader.pages]
        full_text = "\n".join(page_texts)
    with open(outfile, 'w') as file:
        file.write(full_text)


def main():
    parser = argparse.ArgumentParser(description="Read PDF and print text")
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

    extractPdfText(args.in_path, args.out_path)

if __name__ == '__main__':
    main()