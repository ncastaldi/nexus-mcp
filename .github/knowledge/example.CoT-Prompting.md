# A step-by-step breakdown of how to construct an intelligent CoT prompt

## Step 1: Deconstruct the Goal

The objective is to solve a multi-step reasoning problem that a model might otherwise fail if prompted directly. A good problem involves several sequential calculations and requires careful tracking of intermediate results. I will create a word problem that involves calculating a total cost with a discount, and then determining the change from a payment. This is a classic area where models can make simple arithmetic or logical errors, such as applying the discount incorrectly or mixing up the order of operations.[1]

## Step 2: Create High-Quality Few-Shot Exemplars

The core of CoT is showing, not just telling. I will create two distinct exemplars. These examples will demonstrate the desired format: a question, followed by a step-by-step breakdown in natural language that leads to the final answer. The exemplars will solve different, but structurally similar, multi-step problems to establish a robust reasoning pattern.[1]

* **Exemplar 1:** A straightforward problem involving multiplication and addition to calculate a total.
* **Exemplar 2:** A slightly more complex problem involving calculating costs for different items and then finding a total.

### Step 3: Write the Target Question

Finally, I will write the new, unseen question that I want the model to solve. This question will be designed to be solvable by following the reasoning pattern established in the exemplars. It will require the model to:
    1. Calculate the base cost of multiple items.
    2. Correctly apply a conditional discount.
    3. Add the cost of another item.
    4. Calculate the final change from a specific bill.

By providing the exemplars first, the model is primed to break down this new problem into a similar sequence of logical steps, significantly increasing the likelihood of a correct answer.[1]

**Target Question:**

### An Intelligent Example of Chain-of-Thought Prompting

Here is the complete prompt, including the exemplars and the final question, ready to be sent to a large language model.

**Q: A bakery sells muffins for $3 each and cookies for $1.50 each. A customer buys 4 muffins and 6 cookies. What is the total cost?**

**A:** First, calculate the cost of the muffins. The customer buys 4 muffins at $3 each. 4 * $3 = $12.
Next, calculate the cost of the cookies. The customer buys 6 cookies at $1.50 each. 6 * $1.50 = $9.
Finally, add the costs together to find the total. $12 + $9 = $21.
The answer is 21.

**Q: John is buying supplies for his art class. He buys 2 canvases for $12 each and 3 paintbrushes for $4 each. He has a coupon for $5 off his total purchase. How much does he pay?**

**A:** First, calculate the total cost of the canvases. John buys 2 canvases at $12 each. 2 * $12 = $24.
Next, calculate the total cost of the paintbrushes. He buys 3 paintbrushes at $4 each. 3 * $4 = $12.
Then, calculate the total cost before the coupon. $24 + $12 = $36.
Finally, apply the coupon. $36 - $5 = $31.
The answer is 31.
