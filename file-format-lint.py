import re, sys, os, codecs

# Convert the file encoding to the default UTF-8 without BOM.
def check_BOM(filename):
    BUFSIZE = 4096
    BOMLEN = len(codecs.BOM_UTF8)

    with open(filename, "r+b") as fp:
        chunk = fp.read(BUFSIZE)
        if chunk.startswith(codecs.BOM_UTF8):
            i = 0
            chunk = chunk[BOMLEN:]
            while chunk:
                fp.seek(i)
                fp.write(chunk)
                i += len(chunk)
                fp.seek(BOMLEN, os.SEEK_CUR)
                chunk = fp.read(BUFSIZE)
            fp.seek(-BOMLEN, os.SEEK_CUR)
            fp.truncate()
            print("\n" + filename + ": this file's encoding has been converted to UTF-8 without BOM to avoid broken metadata display.")

# Check control characters.
def check_control_char(filename):

    lineNum = 0
    pos = []
    flag = 0

    with open(filename,'r') as file:
        for line in file:

            lineNum += 1

            if re.search(r'[\b]', line):
                pos.append(lineNum)
                flag = 1

    if flag:
        print("\n" + filename + ": this file has control characters in the following lines:\n")
        for cc in pos:
            print("CONTROL CHARACTERS IN L" + str(cc))
        print("Please delete these control characters.")

    return flag


# Check manual line break within a paragraph.
def check_manual_break(filename):

    two_lines = []
    metadata = 0
    toggle = 0
    lineNum = 0
    mark = 0

    with open(filename,'r') as file:
        for line in file:

            lineNum += 1

            # Count the number of '---' to skip metadata.
            if metadata < 2 :
                if re.match(r'(\s|\t)*(-){3}', line):
                    metadata += 1
                continue
            else:
                # Skip tables and notes.
                if re.match(r'(\s|\t)*(\||>)\s*\w*',line):
                    continue

                # Skip html tags and markdownlint tags.
                if re.match(r'(\s|\t)*((<\/*\w+>)|<!--|-->)\s*\w*',line):
                    continue

                # Skip links and images.
                if re.match(r'(\s|\t)*!*\[.+\](\(.+\)|: [a-zA-z]+://[^\s]*)',line):
                    continue

                # Set a toggle to skip code blocks.
                if re.match(r'(\s|\t)*`{3}', line):
                    toggle = abs(1-toggle)

                if toggle == 1:
                    continue
                else:
                    # Keep a record of the current line and the former line.
                    if len(two_lines)<1:
                        two_lines.append(line)
                        continue
                    elif len(two_lines) == 1:
                        two_lines.append(line)
                    else:
                        two_lines.append(line)
                        two_lines.pop(0)

                    # Compare if there is a manual line break between the two lines.
                    if re.match(r'(\s|\t)*\n', two_lines[0]) or re.match(r'(\s|\t)*\n', two_lines[1]):
                        continue
                    else:
                        if re.match(r'(\s|\t)*(-|\+|(\d+|\w{1})\.|\*)\s*\w*',two_lines[0]) and re.match(r'(\s|\t)*(-|\+|\d+|\w{1}\.|\*)\s*\w*',two_lines[1]):
                            continue

                        if mark == 0:
                            print("\n" + filename + ": this file has manual line breaks in the following lines:\n")
                            mark = 1

                        print("MANUAL LINE BREAKS: L" + str(lineNum))
    return mark


if __name__ == "__main__":

    count = 0

    for filename in sys.argv[1:]:
        if os.path.isfile(filename):
            check_BOM(filename)
            flag = check_control_char(filename)
            mark = check_manual_break(filename)
            if mark or flag:
                count+=1

    if count:
        print("\nThe above issues will cause website build failure. Please fix them.")
        exit(1)