### Notes on the processing of the data

**Greetings are used to detect Team Structures**
In our corpus, each letter has a sender and an addressee. Senders may send greetings involving third persons in these letters; such greeting sentences are marked as a whole, with further attributes marked therein:

- attribute _sent_ = {from, to}: Is the sender _forwarding_ (=from) greetings to the addressee, or _asking the addressee to forward_ (=to) greetings to other people?
- attribute _ref_ = the third person(s) mentioned in the greeting

We then define the correspondents' teams as follows:

- If a sender sends greetings _from_ somebody, that person is considered part of the _sender's team_ and gets an edge to the sender.
- If a sender sends greetings _to_ somebody, that person is considered part of the _addressee's team_ and gets an edge to addressee.

**Edges & Filtering**
That gives us a dictionary of undirected team member pairs. If the total edge count (i.e., the count of all greeting-derived mentions) across all years between a given pair of nodes is below 10, that pair and its edges is discarded entirely.

**Nodes & Filtering**
The nodes are the different correspondents in our corpus; the [visualisation](https://github.com/dominic-fischer/dynamic-graph) caps these at the top 50 most prolific writers.
