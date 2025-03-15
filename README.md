# Projeto Spotify: Análise e Playlist de Músicas Curtidas

## Objetivo Principal
Criar uma **playlist personalizada** no Spotify com base nas músicas curtidas, utilizando:
- **API do Spotify**: Para autenticação e coleta de dados.
- **CSV/SQLite**: Para armazenar informações das músicas (nome, artista, popularidade, etc.).
- **Power BI**: Para análise simples (ex: Top 10 músicas mais populares).

## Funcionalidades
1. **Extrair Dados da API**:
   - Acessa suas músicas curtidas via Spotipy.
   - Salva os dados em `musicas_curtidas.csv` e no banco SQLite `spotify_analysis.db`.
2. **Gerar Playlist**:
   - Cria uma playlist automaticamente em sua conta do Spotify com as músicas curtidas.
3. **Análise Visual**:
   - Relatório em Power BI com ranking de popularidade (ex: Top 10).

## Como Executar
### Pré-requisitos
- Conta de desenvolvedor no Para acessar a API do Spotify, visite o [Spotify for Developers](https://developer.spotify.com/). (para obter `CLIENT_ID` e `CLIENT_SECRET`).
- Python 3.x e bibliotecas:
  ```bash
  pip install spotipy pandas sqlite3
