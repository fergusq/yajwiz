import argparse
import re
import sys

import yajwiz

def main():
    parser = argparse.ArgumentParser(description="Klingon grammar checker")
    parser.add_argument("input_file", default="-", help="The text file to be processed")
    parser.add_argument("-I", "--ignore_unknown", action="store_true", help="Ignore unknown word errors")
    parser.add_argument("-w", "--additional_words", help="A comma-separated list of additional words to be added to the dictionary")
    parser.add_argument("-W", "--additional_words_file", help="A file that contains one additional word per line to be added to the dictionary")
    args = parser.parse_args()

    words = set()
    if args.additional_words:
        words |= {"UNKNOWN WORD "+word.strip() for word in args.additional_words.split(",")}
    
    if args.additional_words_file:
        with open(args.additional_words_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    words.add("UNKNOWN WORD "+line)

    if args.input_file and args.input_file != "-":
        input_file = open(args.input_file, "r")
    
    else:
        input_file = sys.stdin
    
    count = 0
    for i, line in enumerate(input_file):
        line = line.strip()
        errors = yajwiz.get_errors(line)
        sentences = re.split(r"[.!?] ", line)
        j = 0
        for error in errors:
            if error.message in words or args.ignore_unknown and error.message.startswith("UNKNOWN WORD"):
                continue
            
            while j+len(sentences[0]) < error.location:
                j += len(sentences[0]) + 2
                sentences.pop(0)
            
            prefix = "Line " + str(i+1) + ": "
            print(prefix + sentences[0])
            print(prefix + " "*(error.location - j) + "^" + error.message)
            print()
            count += 1
    
    print(f"Found {count} errors")
    
    input_file.close()

if __name__ == "__main__":
    main()