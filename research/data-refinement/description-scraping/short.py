from transformers import (
    TokenClassificationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,
)
from transformers.pipelines import AggregationStrategy
import numpy as np

# Define keyphrase extraction pipeline
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs
        )

    def postprocess(self, all_outputs):
        # Get results with scores
        results = super().postprocess(
            all_outputs=all_outputs,
            aggregation_strategy=AggregationStrategy.FIRST,
        )
        # Create a list of tuples (keyword, score)
        scored_keywords = [(result.get("word").strip(), result.get("score")) for result in results]
        # Sort by score in descending order
        sorted_keywords = sorted(scored_keywords, key=lambda x: x[1], reverse=True)
        return sorted_keywords

# Load pipeline
# model_name = "ml6team/keyphrase-extraction-distilbert-inspec"
model_name = "ml6team/keyphrase-extraction-kbir-semeval2017"
extractor = KeyphraseExtractionPipeline(model=model_name)

# Load the aesthetics list from the 'listaesthetics.py' file
from aesthetics_descriptions import aesthetics_descriptions

# Process and summarize all aesthetics descriptions
summarized_aesthetics = []
for aesthetic, description in aesthetics_descriptions[:]:
    ignore = ["Deathrock", "Mallgoth", "Neko", "Neoclassicism", "Nymphet", "Riot Grrrl", "Social Science Academia", "Imperial Aztec"]
    if aesthetic in ignore:
        continue
    print(aesthetic, len(description))
    keyphrases_with_scores = extractor(description)
    # Ensure the aesthetic name is included with a high score
    if aesthetic.lower() not in (keyword_pair[0].lower() for keyword_pair in keyphrases_with_scores):
        keyphrases_with_scores.insert(0, (aesthetic, 100))
    else:
        keyphrases_with_scores = [(keyword, score) for keyword, score in keyphrases_with_scores if keyword.lower() != aesthetic.lower()]
        keyphrases_with_scores.insert(0, (aesthetic, 100))
    # for keyword, score in keyphrases_with_scores:
    #     print(f"Keyword: {keyword}, Score: {score}")
    max_characters = 79
    combined_keywords = []
    keywords = []
    for keyword,score in keyphrases_with_scores:
        keyword = keyword.replace('"', '').replace(',', '').replace('.', '').replace(';', '').replace('()', '').replace(')', '').strip()
        if len(combined_keywords) + len(keyword) + 2 <= max_characters:  # +2 for the comma and space
            combined_keywords += f"{keyword}, "  # Append keyword with a comma
            keywords.append(keyword)
        else:
            break
        
    combinded_string = ", ".join(keywords)
    summarized_aesthetics.append((aesthetic, combinded_string))
    print(f"Summarized '{aesthetic}': {combinded_string}\n")

# Write the summarized aesthetics to a new Python file
output_file = "summarized_aesthetics.py"
with open(output_file, "w") as f:
    f.write("# This file contains summarized aesthetic descriptions\n")
    f.write("aesthetics = [\n")
    for aesthetic, summary in summarized_aesthetics:
        # f.write(f"    (\"{aesthetic}\", \"{summary}\"),\n")
        f.write(f"(\"{summary}\"),\n")
    f.write("]\n")

print(f"Summarized aesthetics have been saved to {output_file}")