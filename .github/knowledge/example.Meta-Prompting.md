# Step-by-Step Generation of an Intelligent Meta Prompt

## 1\. Define the Task Category ($\mathcal{T}$) and Problem Structure

The Meta Prompting framework (modeled as a functor $\mathcal{M}:\mathcal{T}\rightarrow\mathcal{P}$) begins by identifying a category of tasks ($\mathcal{T}$) that share an invariant solution structure.[2]

* **Task Category:** Solving *any* quadratic equation in the form $ax^2 + bx + c = 0$.
* **Invariance:** The fundamental mathematical procedure (calculating the discriminant, applying the quadratic formula) remains constant, regardless of the specific coefficients ($a$, $b$, $c$).

## 2\. Design the Structured Output Template ($\mathcal{P}$)

We design a structured prompt template (an object in the category of prompts, $\mathcal{P}$) that uses a formal syntax (like JSON or XML) to impose a rigid format, ensuring the LLM generates a predictable, parsable, and verifiable output.[2] This structure serves as the scaffolding mechanism.[1]

* **Format:** JSON (ensuring typed fields).
* **Mandated Fields:** `Problem`, `Solution` (containing sequenced steps), and `Final Answer`.

## 3\. Decompose the Universal Reasoning Procedure (Compositionality)

The crucial step is to decompose the task into modular, logical steps that must be executed sequentially.[4, 2] These steps replace the need for content-rich examples found in Few-Shot Prompting.[1, 5]

| Step in $\mathcal{P}$ | Procedural Instruction (How to Think) | Goal |
|---|---|---|
| **Step 1** | Identify coefficients $a$, $b$, and $c$. | Enforce variable isolation. |
| **Step 2** | Compute the discriminant $\Delta=b^{2}-4ac$. | Enforce the first calculation. |
| **Step 3** | Determine the nature of the roots (real, single, or complex) by checking $\Delta$. | Enforce conditional branching logic. |
| **Step 4-6** | Apply the correct formula based on the result of Step 3. | Enforce formula application. |
| **Step 7** | Summarize the roots in a LaTeX-formatted box. | Enforce output formatting/type. |

## 4\. The Final Example: Structured Meta Prompt for Quadratic Equations

This structured meta-prompt provides the complete, reusable "type signature" for solving the quadratic equation category. It guides the model to produce a systematically derived, formatted result for any input values of $a, b, c$.[2]

```json
{
"Task_Category": "Quadratic Equation Solver",
"Problem": "Solve the quadratic equation $ax^{2}+bx+c=0$ for x.",
"Solution_Procedure": {
"Step 1": "Identify the coefficients a, b, and c from the equation.",
"Step 2": "Compute the discriminant using the formula: $\Delta=b^{2}-4ac.$",
"Step 3": "Determine the nature of the roots by checking if $\Delta>0$ (two distinct real roots), $\Delta=0$ (one real root), or $\Delta<0$ (two complex roots).",
"Step 4": "If $\Delta>0$, calculate the two distinct real roots using $x_{1,2}=\frac{-b\pm\sqrt{\Delta}}{2a}.$ ",
"Step 5": "If $\Delta=0$, calculate the single real root using $x=\frac{-b}{2a}.$ ",
"Step 6": "If $\Delta<0$, calculate the complex roots using $x_{1,2}=\frac{-b\pm i\sqrt{|\Delta|}}{2a}.$ ",
"Step 7": "Conclude by summarizing the roots and ensuring the final expression is simplified."
},
"Final Answer_Format": "Present the final answer in a LaTeX-formatted box, using the structure: $\\boxed{x_{1,2} =...}$."
}
```

**Intelligence and Efficiency:**

This example is intelligent because it achieves the core goals of Meta Prompting:

* **Structural Guidance:** It rigorously imposes a multi-step analytical process, forcing the LLM to process the problem methodically.[2]
* **Example-Agnosticism:** No actual numerical example is provided (zero-shot efficacy), saving tokens and preventing the model from relying on analogous content.[1, 2]
* **Compositionality:** It breaks the complex task into simple, reusable computational modules (the steps), aligning with the theoretical modeling of MP as a functor.[2]
