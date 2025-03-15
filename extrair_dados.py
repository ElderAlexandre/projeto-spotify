import spotipy
import sqlite3
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from tqdm import tqdm

# ==============================================
# CONFIGURAÇÃO INICIAL
# ==============================================
load_dotenv(dotenv_path='.env')  # Carrega do arquivo spotify.env

# Configuração da autenticação
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri='http://127.0.0.1:8080',
    scope='user-library-read playlist-modify-private',
    cache_path='.spotipy_cache'
))

# ==============================================
# FUNÇÃO PRINCIPAL: EXTRAIR MÚSICAS CURTIDAS
# ==============================================
def get_saved_tracks():
    """Extrai todas as músicas curtidas com market=BR"""
    all_tracks = []
    offset = 0
    limit = 50  # Máximo permitido pela API
    
    # Primeira chamada para saber o total
    initial = sp.current_user_saved_tracks(limit=1, market='BR')
    total = initial['total']
    
    # Barra de progresso
    with tqdm(total=total, desc="Extraindo músicas") as pbar:
        while True:
            try:
                results = sp.current_user_saved_tracks(
                    limit=limit,
                    offset=offset,
                    market='BR'  # Garante disponibilidade no Brasil
                )
                all_tracks.extend(results['items'])
                offset += limit
                pbar.update(len(results['items']))
                
                if not results['next']:
                    break
                    
            except Exception as e:
                print(f"Erro: {str(e)}")
                break
    
    return all_tracks

# ==============================================
# FUNÇÃO: CRIAR PLAYLIST
# ==============================================
def create_playlist(tracks):
    """Cria playlist e adiciona músicas"""
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(
        user=user_id,
        name="[AUTO] Músicas Curtidas",
        public=False,
        description=f"Playlist gerada em {pd.Timestamp.now().strftime('%Y-%m-%d')} com {len(tracks)} músicas"
    )
    
    # Preparar URIs em lotes de 100
    track_uris = [t['track']['uri'] for t in tracks]
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i:i+100]
        sp.playlist_add_items(playlist['id'], batch)
    
    return playlist

# ==============================================
# FUNÇÃO: SALVAR DADOS PARA ANÁLISE
# ==============================================
def save_for_analysis(tracks, playlist):
    """Salva dados em SQL e CSV"""
    # Processar dados
    df = pd.DataFrame([{
        'id_musica': t['track']['id'],
        'nome': t['track']['name'],
        'artista': t['track']['artists'][0]['name'],
        'album': t['track']['album']['name'],
        'duracao_ms': t['track']['duration_ms'],
        'explicita': t['track']['explicit'],
        'popularidade': t['track']['popularity'],
        'data_adicao': pd.to_datetime(t['added_at']),
        'id_playlist': playlist['id']
    } for t in tracks])
    
    # Salvar em SQLite
    with sqlite3.connect('spotify_analysis.db') as conn:
        df.to_sql('tracks', conn, if_exists='replace', index=False)
    
    # Salvar em CSV
    df.to_csv('musicas_curtidas.csv', index=False)
    
    return df

# ==============================================
# EXECUÇÃO PRINCIPAL
# ==============================================
if __name__ == "__main__":
    print("🚀 Iniciando processo...")
    
    # Passo 1: Extrair músicas
    tracks = get_saved_tracks()
    print(f"✅ {len(tracks)} músicas encontradas!")
    
    # Passo 2: Criar playlist
    if tracks:
        playlist = create_playlist(tracks)
        print(f"🎧 Playlist criada: {playlist['external_urls']['spotify']}")
        
        # Passo 3: Salvar dados
        df = save_for_analysis(tracks, playlist)
        print(f"📊 Dados salvos: {len(df)} registros")
        
        # Dicas para análise
        print("\n🔍 Para análise no Power BI:")
        print("1. Conecte ao arquivo 'spotify_analysis.db'")
        print("2. Use a tabela 'tracks'")
        print("3. Campos úteis: nome, música, duracao_ms, data_adicao, popularidade")
    else:
        print("⚠️ Nenhuma música encontrada para processar!")