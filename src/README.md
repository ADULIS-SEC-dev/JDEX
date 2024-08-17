# Abstract
* Proof-Of-Concept [0.1]
	* Initial: Telegram-based, Blockchain DB iteration (Blockchain with RDB).
		* Creates a Block/s w/ (and writes it into the DB). No data abstraction (i.e. the Blocks do not carry user-requested data, like transactions, etc.). Columns:
			* Id.col (primary key) -> Irrelevant to the Block abstraction.
			* timestamp.col
			* _Username.col
			* Username.col
			* Hash.col
			* prevHash.col

---
# Setting up the PoC
* ...
