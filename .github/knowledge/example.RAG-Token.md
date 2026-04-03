# Intelligent RAG Example: Generating a Question from an Answer

**Scenario:** Jeopardy Question Generation

**Input (The Answer/Topic, $x$):**
$$\text{"Hemingway"}$$ [1]

**Goal:** The RAG system must generate a question that is factually grounded and specific enough to uniquely identify Ernest Hemingway, drawing from its external knowledge base.

## Step 1: Query Encoding and Non-Parametric Retrieval

1. **Query Encoding:** The user's input, "Hemingway," is processed by the specialized **query encoder ($BERT_{q}$)**, which converts the input text into a dense vector embedding.[1]
2. **Maximum Inner Product Search (MIPS):** This query vector is used to perform a fast approximate search (MIPS) against the **non-parametric memory** (a dense vector index of 21 million Wikipedia chunks).[1]
3. **Retrieval Result:** The system retrieves the top $K$ documents (e.g., 10 documents) that are semantically closest to the query. For this example, let's focus on two specific passages that contain different facts:

    * **Document $z_1$:** Mentions: *"His wartime experiences formed the basis for his novel 'A Farewell to Arms' (1929)..."*.[1]
    * **Document $z_2$:** Mentions: *"...artists of the 1920s 'Lost Generation' expatriate community. His debut novel, 'The Sun Also Rises', was published in 1926."*.[1]

## Step 2: The RAG-Token Generator Begins

The generator (BART, the parametric memory) begins producing the output sequence. The RAG-Token model computes the probability of the next token by marginalizing over all retrieved documents at *each step*.[1]

**Output Tokens 1-5 (Generic Phrase):**

| **Token** | **Retrieved Context Domination** | **Action/Insight** |
| :---: | :---: | :--- |
| **This** | (Flat Posterior) | The initial tokens are drawn primarily from the model's parametric memory (its core LLM training) to construct a grammatically correct start.[1] |
| **author** | (Flat Posterior) | |
| **of** | (Flat Posterior) | |

## Step 3: Dynamic Retrieval and Fact Insertion (Document $z_2$ Dominates)

As the generation progresses, the model determines that it needs a specific fact to continue. It calculates the likelihood of generating certain fact-related tokens based on the available documents.

| **Token** | **Retrieved Context Domination** | **Action/Insight** |
| :---: | :---: | :--- |
| **"The** | **Document $z_2$ (High)** | The model implicitly recognizes that Document $z_2$ contains a strongly supported, specific fact about *"The Sun Also Rises"*. It uses the content of $z_2$ as the primary context to generate the next sequence of tokens.[1] |
| **Sun** | **Document $z_2$ (High)** | |
| **Also** | **Document $z_2$ (High)** | |
| **Rises"** | **Document $z_2$ (High)** | |

## Step 4: Relying on Parametric Memory for Completion

After the model generates the sequence `"The Sun Also Rises"`, the influence of Document $z_2$ on the *next* tokens begins to flatten.[1]

| **Token** | **Retrieved Context Domination** | **Action/Insight** |
| :---: | :---: | :--- |
| **is** | (Flat Posterior) | The model's implicit parametric knowledge is sufficient to complete the well-known connecting phrase *"is a novel by this author of..."* without needing continuous explicit grounding.[1] |
| **a** | (Flat Posterior) | |

## Step 5: Synthesis and Context Switch (Document $z_1$ Dominates)

To make the question even more specific and factual, the model uses the RAG-Token mechanism to dynamically incorporate a second, distinct fact from a different retrieved document ($z_1$).

| **Token** | **Retrieved Context Domination** | **Action/Insight** |
| :---: | :---: | :--- |
| **"A** | **Document $z_1$ (High)** | The model shifts its focus to Document $z_1$, which mentions the second fact (*"A Farewell to Arms"*). This switch enables **knowledge synthesis**, a core strength of RAG, allowing it to combine multiple pieces of evidence into one coherent response.[1] |
| **Farewell** | **Document $z_1$ (High)** | |
| **to** | **Document $z_1$ (High)** | |
| **Arms"** | **Document $z_1$ (High)** | |

**Final Generated Question:**
$$\text{"This author of 'The Sun Also Rises' is a novel by this author of 'A Farewell to Arms'"}$$

**Intelligent Outcome:**
The RAG-Token model successfully synthesized two separate facts from two different knowledge passages ($z_1$ and $z_2$) to create a highly specific and factually grounded question, a capability that purely parametric models often struggle with and one that an extractive model could not achieve.[1] This synthesis demonstrates how RAG strategically leverages both its explicit knowledge base (the non-parametric memory) and the LLM’s linguistic fluency (the parametric memory) to produce a superior, more diverse, and more factual output.[1]
