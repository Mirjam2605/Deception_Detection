import spacy
import string

def to_logical_form(text, statement_map=None, negations=None, current_label=None):
    # Load the English NLP model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    logical_connectors = [" so ", "therefore", "thus", "hence", "as a result", "due to", "consequently"]

    # Create statement map and negation if not passed in function.
    if statement_map is None:
        statement_map = {}
    if negations is None:
        negations = {}

    if current_label is None:
        current_label = 0 # start with letter a

    # results
    logical_forms = []

    for sent in doc.sents:
        # lowercasing and punctuation removal
        stripped_sent = ' '.join([token.text for token in sent if token.pos_ != 'PUNCT']).strip().lower()

        connector_found = False

        for connector in logical_connectors:
            if connector in stripped_sent:
                connector_found = True
                parts = stripped_sent.split(connector)
                for i, part in enumerate(parts):
                    part_doc = nlp(part.strip())
                    part_negation = any(token.dep_ == 'neg' for token in part_doc)
                    part_base_sent = ' '.join([token.text for token in part_doc if
                                               token.pos_ != 'PUNCT' and token.dep_ != 'neg']).strip().lower()

                    if part_base_sent not in statement_map:
                        statement_map[part_base_sent] = string.ascii_lowercase[current_label]
                        current_label += 1

                    part_label = statement_map[part_base_sent]
                    negations[part_label] = part_negation

                    if i == 0:
                        # cause
                        cause_label = part_label
                        cause_negation = part_negation
                    else:
                        effect_label = part_label
                        effect_negation = part_negation

                cause_form = f"not {cause_label}" if cause_negation else cause_label
                effect_form = f"not {effect_label}" if effect_negation else effect_label
                logical_forms.append(f"{cause_form} => {effect_form}")
                break  # Only process one connector

        if not connector_found:
            # If no connector is found we process it as statement
            negation = any(token.dep_ == 'neg' for token in sent)
            base_sent = ' '.join(
                [token.text for token in sent if token.pos_ != 'PUNCT' and token.dep_ != 'neg']).strip().lower()

            if base_sent not in statement_map:
                print(current_label)
                statement_map[base_sent] = string.ascii_lowercase[current_label]
                current_label += 1

            base_label = statement_map[base_sent]
            negations[base_label] = negation
            print(connector_found, base_sent, base_label, statement_map[base_sent])

            logical_form = f"not {base_label}" if negation else base_label
            logical_forms.append(logical_form)

    return logical_forms, statement_map, negations, current_label
