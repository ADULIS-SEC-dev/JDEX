#!/usr/bin/env python3.11

"""
	* Copyright(c) 2024, ADULIS(R) SECURITIES. All rights reserved.
    * Copyright(c) JEGOL(TM) Decentralized Exchange.
    
    * Proof-Of-Concept
		* Initial: Telegram-based, Blockchain DB iteration (Blockchain with RDB).
			* Creates a Block/s w/ (and writes it into the DB). No data abstraction (i.e. the Blocks do not carry user-requested data, like transactions, etc.)
				* Id.col (primary key) -> Irrelevant to the Block abstraction.
				* timestamp.col
				* _Username.col
				* Username.col
				* Hash.col
				* prevHash.col
"""

