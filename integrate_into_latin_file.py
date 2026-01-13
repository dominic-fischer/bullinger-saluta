
import sys
sys.stdout.reconfigure(encoding="utf-8")

with open("Latin_Files/new_final_gpt_directionality_analysis.txt", "r", encoding="utf-8") as infile:
    original_lines = infile.readlines()

with open("GPT_analysed_sentences_LATIN.txt", "r", encoding="utf-8") as f:
    corrected_lines = f.readlines()

original_lines = [l.split("\t") for l in original_lines]
corrected_lines = [l.split("\t") for l in corrected_lines]
final_lines = []

counter = 0

for t1, t2 in original_lines:
    file = t1
    line = t2.split('">')[0] + ">"
    is_in_corr = False
    for f1, f2 in corrected_lines:
        file_corrected = f1
        line_corrected = f2.split('">')[0] + ">"
        if file == file_corrected and line == line_corrected:
            final_lines.append([f1, f2])
            is_in_corr = True
            counter += 1
            break
    if not is_in_corr:
        final_lines.append([t1, t2])

print(counter)
print(len(final_lines))




with open("NEW_integrated_LATIN.txt", "w", encoding="utf-8") as outfile:
    for f1, f2 in final_lines:
        outfile.write(f1 + "\t" +  f2)
