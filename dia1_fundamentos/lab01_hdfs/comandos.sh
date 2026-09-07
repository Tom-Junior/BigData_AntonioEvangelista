#!/usr/bin/env bash
# Rota B: armazenamento local equivalente ao landing zone.
mkdir -p bigdata/raw bigdata/bronze bigdata/silver bigdata/gold
cp avaliacao_transactions.csv bigdata/raw/
