# **Intelligent Example: Solving Mini Crosswords with ToT and Backtracking**

The objective is to fill a $5\times5$ grid by finding ten words that satisfy both the horizontal and vertical clues (lexical, spatial, and deductive reasoning are all required).

## **Problem Setup**

* **Task:** $5\times5$ Mini Crossword (20 questions/clues in total).
* **Goal:** Fill the entire grid correctly.
* **Thought Decomposition:** Each "thought" is the placement of a single word/clue filling (e.g., h1. TASKS; v5. NALED). The thoughts are sequenced based on priority queue, creating up to 10 intermediate steps.[1]
* **Search Algorithm:** Depth-First Search (DFS). This prioritizes exploring one path completely before trying another.[2, 1]
* **Heuristic Evaluation (Pruning):** At each step, the LLM is prompted to evaluate *all remaining unfilled clues* based on the current letter constraints. The output is a confidence score or a classification (e.g., "possible," "impossible").[1]

***

## **Step-by-Step ToT Execution (Demonstrating Backtracking)**

Let's assume the LLM has already successfully filled **h1. TASKS** and is now at a search node (State $s_{2}$).

### **Step 1: Thought Generation (Prioritization)**

The LLM is prompted to generate and prioritize candidates for the next word/clue to fill, considering the existing letter constraints (the 'A' from T**A**SKS constrains one vertical clue, for instance).

| Clue/Thought | Proposed Word | LLM Confidence (Heuristic) | Search Action |
| :--- | :--- | :--- | :--- |
| **h2.** [Clue] | **MOTOR** | High | **Prioritize.** Select for deep exploration. |
| **v3.** [Clue] | **STRING** | Medium | Keep as alternative. |
| **h4.** [Clue] | **SALON** | High | Keep as alternative. |

**Search Action:** DFS commits to the **h2. MOTOR** path first.

### **Step 2: Deep Exploration (Fatal Error)**

The system now expands the tree deeply along the chosen path. After placing h2. MOTOR, a new constraint is created (the 'T' from MOTOR constrains a different vertical clue). The LLM proposes and places the next thought, for instance, **v1. TENETS**.

| Thought Generated | Partial Solution State | Search Action |
| :--- | :--- | :--- |
| **v1. TENETS** | Grid now contains TASKS, MOTOR, and TENETS | Continue deep search. |

### **Step 3: State Evaluation and Pruning**

The LLM is then asked to evaluate the viability of the *entire remaining problem* from this new state ($s_{3}$). It examines all un-filled horizontal and vertical clues against the letters placed so far.

The LLM finds that, due to the letter placement conflict between h1, h2, and v1, one remaining vertical clue, **v5.**, now has the mandatory constraint: S\_R\_D\_.

| Remaining Clue | Constraint | LLM Value Prompt Result | Pruning Trigger |
| :--- | :--- | :--- | :--- |
| v5. Desiccator... | S\_R\_D\_ | **Impossible** [1] | **Pruning Activated.** |

The LLM determines that no known word can satisfy the S\_R\_D\_ constraint given the clue, rendering the current path a "dead-end." This is an explicit, language-based heuristic determination.[1]

### **Step 4: Backtracking**

Because the current state is deemed "impossible," the DFS algorithm executes the crucial ToT mechanism: **Backtracking**.[1]

1. The entire sub-tree stemming from **v1. TENETS** is pruned and discarded.
2. The system reverts the search state back to the parent node, where only **h1. TASKS** and **h2. MOTOR** were placed.
3. The search mechanism marks **v1. TENETS** as a failed branch and selects the next alternative from the queue at that level (Step 2). If no alternatives exist, it backtracks again to the previous parent (State $s_{2}$ before *any* move was made from it).

**Intelligence Demonstrated:**

The key advantage here is the LLM's capacity to recognize a long-term failure immediately after a local step, prompting a structural correction to the problem-solving process.[1]

* **Linear CoT Failure:** A linear Chain-of-Thought process would have continued generating tokens sequentially, amplifying the error from the "impossible" constraint until the whole sequence was produced and failed.[1]
* **ToT Success:** ToT uses its **deliberate self-evaluation** (System 2 reasoning) to trigger a global search control function (backtracking), thus saving computational steps and efficiently recovering from the local error to search an alternative, viable path.[2, 1] The research confirmed this capability is indispensable for complex planning: removing the backtracking feature caused the success rate to plummet from 60% to only 20% on the Mini Crosswords task.[1]
