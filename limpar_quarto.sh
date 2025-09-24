#!/bin/bash
# Script para limpar cache do Quarto e recompilar o site

echo "🧹 Limpando cache do Quarto..."
rm -rf .quarto/ _freeze/

echo "⚡ Recompilando o projeto..."
quarto render --no-cache

echo "✅ Concluído!"
