# **ReAct Example: Multi-Hop Knowledge Retrieval**

| Component | Content | Analysis of Synergy |
|---|---|---|
| **Question** | What instrument did the composer who created the soundtrack for the 1999 film *The Mummy* study at the Royal College of Music? | **Initial Goal:** A two-step query requiring identifying the composer, then finding their specific educational history from an external source. |
| **Thought 1** | I need to decompose the question. First, I must find the composer of *The Mummy* (1999). Then, I must search for what instrument that person studied at the Royal College of Music. | **Reason-to-Act:** The thought decomposes the complex goal into two manageable subtasks and sets the plan for the first action.[2] |
| **Act 1** | `Search` | The action executes the first step of the plan derived from Thought 1. |
| **Observation 1** | The score for the 1999 film *The Mummy* was composed by Jerry Goldsmith. | The external environment returns a verifiable fact, which now grounds the next phase of reasoning.[2] |
| **Thought 2** | The composer is Jerry Goldsmith. I need to search for Jerry Goldsmith's connection to the Royal College of Music and determine the instrument he studied. | **Act-to-Reason:** The thought extracts the key entity ("Jerry Goldsmith") from the observation and uses it to update the task goal and formulate the next action.[2] |
| **Act 2** | `Search` | The action is more specific, guided by the updated information in Thought 2. |
| **Observation 2** | Jerry Goldsmith briefly attended the Royal College of Music in London, where he studied composition and conducting. | This observation confirms his attendance but does not provide the specific instrument requested in the question. |
| **Thought 3** | The general search did not yield the specific instrument. I need to refine my focus and use a more targeted action, perhaps a `Lookup` on the confirmed page to search for the keyword "instrument" or "piano/percussion." | **Reason-to-Act (Exception Handling):** The thought recognizes that the previous action failed to provide the necessary detail, adjusts the plan, and specifies a new, refined action to overcome the non-informative observation.[2] |
| **Act 3** | `Lookup [percussion or piano]` | The action targets specific keywords based on the revised strategy in Thought 3. |
| **Observation 3** | (Result 1/1) During his time at the Royal College of Music, Goldsmith focused primarily on percussion instruments, but also briefly studied piano. | The lookup action retrieves the necessary specific detail. |
| **Thought 4** | The information is now complete. The composer is Jerry Goldsmith, and he focused on percussion instruments at the Royal College of Music. I can now finalize the answer. | **Act-to-Reason & Synthesis:** The thought processes the final, grounded observation and synthesizes the multi-hop answer.[2] |
| **Act 4** | `Finish [Percussion instruments]` | The final action terminates the process with the verified answer. |
