import ollama

def give_tags(para, n=5):

    prompt = f"""Generate {n} relevant tags for the following paragraph:\n{para}\nWords in tags must be space separated only. Do
               not assume anything other than what is given in the paragraph, but you can use similar words and context clues
               to generate tags. Do not make any tag more than one word long. 
               If you have seen this paragraph before, generate the same tags that you had generated earlier.
               Do not put anything in parentheses for the tags you generate.\nTags:"""

    reply = ollama.chat(model="mistral:7b-instruct", 
                        messages=[{"role": "user", "content": prompt}])
    result = reply['message']['content']

    tags = result.split("Tags:")[-1].strip().replace("\n", ",").split(",")
    #print(tags)
    '''format_tags = []
    for i in tags:
        i = i.strip(" .)")
        if i and i[0].isdigit() and '.' in tag:
            i = i.split('.', 1)[-1].strip()
        format_tags.append(i)'''

    return tags[:n]

#driver code
para = """The old lighthouse keeper, Silas, swore the salt spray had woven itself into his bones. 
Each morning, the gulls' cries were his alarm, a raucous chorus that blended with the rhythmic crash 
of waves against the jagged cliffs. He'd spent decades tending the lonely tower, its beam a faithful 
sentinel against the endless, churning grey. Today, a peculiar stillness hung in the air, a hush before 
an unseen storm. The sea, usually a restless beast, lay flat and oily, reflecting the bruised purple 
of the pre-dawn sky. A single, dark shape bobbed in the distance, a stark contrast against the 
unnatural calm. Silas squinted, his weathered hands gripping the railing, a sense of unease creeping 
into his heart. It was too large to be a buoy, too still to be a boat. He reached for his telescope, 
the brass cold against his skin, and focused the lens. What he saw made his breath catch in his throat: 
a massive, obsidian-like structure, its surface smooth and featureless, rising from the silent sea.
"""

tags = give_tags(para)
print("Tags:")
for i, tag in enumerate(tags, start = 1):
    tag = tag.lstrip()
    print(f"{i}.{tag}")