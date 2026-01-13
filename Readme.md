
### Notes on the processing of the data

**Filtering**
- If the total of edges across all years between a given pair of nodes is below 10, that pair and its edges is discarded entirely

**Edges**
- Only actual greetings currently count as edges (the amount of letters between two people is disregarded)
- The edges are undirected, i.e. all greetings exchanged between two nodes in a given year form an edge together
- The thickness of that edge corresponds to the number of exchanged greetings

**Nodes**
- The radius of a node is proportional to the amount of letters of that person in the entire Bullinger Corpus (~ the person's significance wrt. to Bullinger). This proportioning starts from the second-most prolific writer, as Bullinger himself is an outlier. Bullinger's radius is clamped to the maximum, i.e. that writer's size.
- Node filtering (Top N) is based on radius size
