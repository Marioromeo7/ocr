def o(img_path):
    from paddleocr import PaddleOCR
    languages = ["en", "arabic"]
    # img_path="C:/Users/Mario/OneDrive/Desktop/test18.png.jpg"
    # for lang in languages:
    #     ocr = PaddleOCR(use_angle_cls=True, lang=lang)
    #     result = ocr.ocr(img_path, cls=True)
        
    #     print(f"Results for {lang}:")
    #     for line in result:
    #         for word in line:
    #             print(f"Text: {word[1][0]}, Confidence: {word[1][1]}")
    # ocr2=PaddleOCR(use_angle_cls=True, lang="en,arabic")
    # res=ocr2.ocr(img_path, cls=True)
    # for line in res:
    #         for word in line:
    #             print(f"Text: {word[1][0]}, Confidence: {word[1][1]}")
    words_data=[]
    for lang in languages:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        result = ocr.ocr(img_path, cls=True)
        for line in result:
            for word in line:
                # Extract the bounding box; here we use the top-left coordinate as an anchor.
                box = word[0]
                x = min(pt[0] for pt in box)
                y = min(pt[1] for pt in box)
                text = word[1][0]
                words_data.append((x, y, text))

    # Now sort words_data: first by the y-coordinate (top to bottom) and then by the x-coordinate (left to right)
    # sorted_words = sorted(words_data, key=lambda tup: (tup[1], tup[0]))

    # Combine the sorted words into a single text string
    # final_text = " ".join(text for (_, _, text) in sorted_words)
    # print("OCR Result:")
    # print(final_text)
    def group_words_by_line(words, y_threshold=10):
        """
        Groups words (each as a tuple (x, y, text)) into lines.
        Words with y-coordinates within y_threshold pixels are grouped together.
        """
        # Sort words by y coordinate (top to bottom)
        sorted_words = sorted(words, key=lambda tup: tup[1])
        lines = []
        current_line = []
        current_y = None

        for word in sorted_words:
            x, y, text = word
            if not current_line:
                current_line.append(word)
                current_y = y
            else:
                # If the y-coordinate difference is less than the threshold, consider it the same line
                if abs(y - current_y) < y_threshold:
                    current_line.append(word)
                    # Update the average y for the current line (optional for a more robust grouping)
                    current_y = sum(w[1] for w in current_line) / len(current_line)
                else:
                    lines.append(current_line)
                    current_line = [word]
                    current_y = y
        if current_line:
            lines.append(current_line)
        return lines

    # Group the words by line
    lines = group_words_by_line(words_data, y_threshold=10)

    # For each line, sort the words by their x-coordinate (left to right) and join them
    final_text_lines = []
    for line in lines:
        sorted_line = sorted(line, key=lambda tup: tup[0])
        # Join words with a space; adjust as needed
        line_text = " ".join(word[2] for word in sorted_line)
        final_text_lines.append(line_text)

    # Combine the lines with newlines to form the final output
    # final_text = "\n".join(final_text_lines)
    # import re
    # # vendor_pattern=re.compile(r"^([\u0621-\u064A]+)\s*[a-zA-Z]+(\s*[\u0621-\u064A]+\s*[\u0621-\u064A]+\s*)")
    # invoice_pattern = re.compile(r"(((\d+)\sهب  ةروتاف)|((\d+)\s*\d*\s*ةروتافلا)|((\d+)[\u0621-\u064A\s]*دوكلا)|((\d+)[\u0621-\u064A\s]*عيب ةروتاف))")
    # total_pattern=re.compile(r"ةروتافلا ىقاص\s*\d+\s*\d+\s*(\d+.\d+)")
    # date_pattern    = re.compile(r"\s*(\d+/\d+/\d+)")
    # amount_pattern  = re.compile(r"ةروتافلا ىقاص \s*(\d+)")
    # customer_pattern = re.compile(r"\s*([\u0621-\u064A]+) ص ليمعلا مسا\s*")

    # # Search for patterns in the OCR text
    # vendor_match=vendor_pattern.search(final_text)
    # invoice_match = invoice_pattern.search(final_text)
    # total_match=total_pattern.search(final_text)
    # date_match    = date_pattern.search(final_text)
    # amount_match  = amount_pattern.search(final_text)
    # customer_match = customer_pattern.search(final_text)

    # Extract values (if found)
    # vendor_value=vendor_match.group(1) if vendor_match else None
    # vendor_value2=vendor_match.group(2) if vendor_match else None
    # invoice_value = invoice_match.group(3) if invoice_match else None
    # for i in range(3,10,2):
    #     invoice_value = invoice_match.group(i) if invoice_match else None
    #     if invoice_value!=None:
    #         break
    # # total_value=total_match.group(1) if total_match else None
    # # date_value    = date_match.group(1) if date_match else None
    # # amount_value  = amount_match.group(1) if amount_match else None
    # # customer_value = customer_match.group(1).strip() if customer_match else None

    # # Print the parsed values
    # print("Parsed OCR Values:")
    # # print("vendor:",vendor_value+vendor_value2)
    # print("Invoice:", invoice_value)
    # # print("total:",total_value)
    # # print("Date:", date_value)
    # # print("Amount:", amount_value)
    # # print("Customer:", customer_value)
    import re
    def isfloat(word):
        pattern=r"\d+.\d+"
        return bool(re.search(pattern,word))
    def matchingfn(word,lst,threshold=.50):
        v=[]
        for w in lst:
            cor_count=0
            cur_w=0
            for i in word:
                if cor_count>=len(w):
                    break
                if i==w[cur_w]:
                    cur_w+=1
                    cor_count+=1
            v.append(cor_count/len(word))
        if max(v)>threshold:
            return True
        return False
    def matchingfn(word,lst,threshold=.50):
        v=[]
        for w in lst:
            cor_count=0
            cur_w=0
            for i in word:
                if cor_count>=len(w):
                    break
                if i==w[cur_w]:
                    cur_w+=1
                    cor_count+=1
            v.append(cor_count/len(word))
        if max(v)>threshold:
            return True
        return False
    values=[]
    valamount=[]
    lst=['ةروتاف','دوك']
    for line in range(len(lines)):
        for i in range(len(lines[line])):
            if matchingfn(lines[line][i][2],lst) :
                for x in lines[line]:
                    if x[2].isdigit():
                        values.append(x[2])
                for x in lines[line+1]:
                    if x[2].isdigit():
                        values.append(x[2])
                for x in lines[line+2]:
                    if x[2].isdigit():
                        values.append(x[2])
    #         if lines[line][i][2] in ['ةروتافلا ىقاص','ةصلاخ ةروتافلا','ةروتافلا']:
    #                print(lines[line+1])
    #             if isfloat(lines[line+1][i-1][2]):
    #                 valamount.append(lines[line+1][i-1][2])
    #             elif isfloat(lines[line+2][i-2][2]):
    #                 valamount.append(lines[line+2][i-2][2])
    return values
