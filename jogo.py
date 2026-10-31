import pygame
import sys
import os

# 1. Configurações Iniciais e Janela
pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Fuga de Casa: 198X - Edição de Suspense")
relogio = pygame.time.Clock()

# Cores de Interface e Fallback
COR_TEXTO = (251, 242, 218)     
COR_CAIXA = (20, 16, 26)        
COR_AVISO = (255, 230, 100)
COR_INVENTARIO = (45, 40, 60)

# 2. Sistema de Carregamento de Imagens Reais (Com Fallback Seguro)
def carregar_imagem(nome_arquivo, largura, altura, cor_fallback):
    if os.path.exists(nome_arquivo):
        img = pygame.image.load(nome_arquivo).convert_alpha()
        return pygame.transform.scale(img, (largura, altura))
    else:
        surface = pygame.Surface((largura, altura))
        surface.fill(cor_fallback)
        return surface

# Carregando os elementos visuais realistas
img_fundo = carregar_imagem("fundo_sala.jpg", 800, 600, (40, 26, 44))
img_garota = carregar_imagem("garota.png", 40, 65, (255, 119, 168))
img_sofa = carregar_imagem("sofa.png", 180, 100, (62, 39, 49))
img_estante = carregar_imagem("estante.png", 150, 120, (160, 91, 51))
img_armario = carregar_imagem("armario.png", 120, 130, (100, 70, 50))
img_gavetas = carregar_imagem("gavetas.png", 90, 90, (130, 90, 60))

# 3. Estado do Jogo e Narrativa
historia_estado = "inicio" 
tem_chave = False
texto_atual = "Eles se trancaram no quarto para brigar... É a minha chance. Preciso usar a lanterna para tatear no escuro, chegar perto de um móvel e apertar [E] para procurar a chave de casa!"

TEMPO_LIMITE_SEGUNDOS = 120
frames_contados = 0
perto_de_objeto = None  

# 4. Criação da Máscara de Escuridão (Efeito Lanterna)
# Criamos uma superfície preta do tamanho da tela para agir como a escuridão da noite
superficie_escuridao = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)

def atualizar_lanterna(pos_x, pos_y):
    # Preenche a tela inteira com um preto quase opaco (transparência 240 de 255)
    superficie_escuridao.fill((10, 8, 15, 242))
    
    # Desenha o foco da lanterna (um círculo totalmente transparente no centro do jogador)
    # Raio de 110 pixels para dar um clima tenso de visão limitada
    pygame.draw.circle(superficie_escuridao, (0, 0, 0, 0), (pos_x, pos_y), 110)
    
    # Cria uma borda suave de penumbra ao redor do círculo principal
    for raio in range(110, 140, 4):
        alfa = int((raio - 110) / 30 * 242)
        pygame.draw.circle(superficie_escuridao, (10, 8, 15, alfa), (pos_x, pos_y), raio, 4)

# 5. Classes do Jogo
class GarotinhaReal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_garota
        self.rect = self.image.get_rect()
        self.rect.center = (400, 420) 
        self.velocidade = 3.5

    def update(self, teclas):
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.rect.x += self.velocidade
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.rect.y -= self.velocidade
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.rect.y += self.velocidade
        self.rect.clamp_ip(tela.get_rect())

class MovelReal(pygame.sprite.Sprite):
    def __init__(self, x, y, imagem, nome):
        super().__init__()
        self.image = imagem
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.nome = nome

# Inicializando o layout realista da sala
garota = GarotinhaReal()
sofa = MovelReal(310, 360, img_sofa, "sofa")
estante = MovelReal(60, 150, img_estante, "estante")       # Onde a chave real está escondida
armario = MovelReal(280, 140, img_armario, "armario")     
gavetas = MovelReal(480, 160, img_gavetas, "gavetas")       
porta_saida = MovelReal(680, 150, pygame.Surface((60, 140)), "porta") 
porta_saida.image.fill((90, 40, 40)) 

sprites = pygame.sprite.Group()
sprites.add(sofa, estante, armario, gavetas, porta_saida, garota)

# 6. Interface de Texto, Inventário e Fontes
try:
    fonte = pygame.font.SysFont("Courier New", 18, bold=True)
    fonte_tempo = pygame.font.SysFont("Courier New", 20, bold=True)
    fonte_inv = pygame.font.SysFont("Courier New", 14, bold=True)
except:
    fonte = pygame.font.Font(None, 22)
    fonte_tempo = pygame.font.Font(None, 24)
    fonte_inv = pygame.font.Font(None, 16)

def desenhar_interface(texto, tempo_restante, interagir_aviso, possui_chave):
    # --- 1. Caixa Principal de Diálogo ---
    caixa = pygame.Rect(20, 460, 760, 120)
    pygame.draw.rect(tela, COR_CAIXA, caixa)
    pygame.draw.rect(tela, COR_TEXTO, caixa, 3) 
    
    # Cronômetro
    minutos = tempo_restante // 60
    segundos = tempo_restante % 60
    str_tempo = f"TEMPO ANTES QUE ELES SAIAM DO QUARTO: {minutos:02d}:{segundos:02d}"
    cor_timer = (230, 70, 70) if tempo_restante <= 20 else COR_TEXTO
    tela.blit(fonte_tempo.render(str_tempo, True, cor_timer), (40, 470))
    
    # Mensagem de alerta flutuante para apertar "E"
    if interagir_aviso:
        aviso_texto = f"Pressione [E] para revistar o(a) {interagir_aviso}"
        superficie_aviso = fonte_tempo.render(aviso_texto, True, COR_AVISO)
        tela.blit(superficie_aviso, (LARGURA // 2 - superficie_aviso.get_width() // 2, 425))
    
    # Quebra de texto automática na caixa de diálogos
    palavras = texto.split(' ')
    linhas = ""
    linha_atual = ""
    for palavra in palavras:
        if fonte.size(linha_atual + palavra) < 710:
            linha_atual += palavra + " "
        else:
            linhas.append(linha_atual)
            linha_atual = palavra + " "
    linhas.append(linha_atual)

    y_offset = 505
    for i, linha in enumerate(linhas):
        if i < 2: 
            tela.blit(fonte.render(linha, True, COR_TEXTO), (40, y_offset))
            y_offset += 25

    # --- 2. Painel Visual do Inventário (Canto Superior Direito) ---
    caixa_inv = pygame.Rect(620, 20, 160, 50)
    pygame.draw.rect(tela, COR_INVENTARIO, caixa_inv)
    pygame.draw.rect(tela, COR_TEXTO, caixa_inv, 2)
    tela.blit(fonte_inv.render("MOCHILA:", True, COR_TEXTO), (630, 25))
    
    if possui_chave:
        # Mostra o item em verde brilhante se coletado
        tela.blit(fonte_inv.render("[ CHAVE DE CASA ]", True, (100, 255, 100)), (630, 45))
    else:
        # Vazio se não tiver pego
        tela.blit(fonte_inv.render("( Vazia )", True, (140, 140, 140)), (630, 45))

# 7. Loop Principal do Jogo
rodando = True
while rodando:
    relogio.tick(60) 
    
    # Captura de Eventos de Teclado (Aperto único da tecla E)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_e and historia_estado not in ["fugiu", "game_over"]:
                if perto_de_objeto:
                    if perto_de_objeto == "estante" and historia_estado == "inicio":
                        texto_atual = "(Você vasculha as prateleiras de madeira...) Encontrei! A chave pesada de ferro estava escondida atrás do toca-discos antigos! Sua mochila brilha. Vá para a porta!"
                        tem_chave = True
                        historia_estado = "com_chave"
                        
                    elif perto_de_objeto == "armario" and historia_estado == "inicio":
                        texto_atual = "(Você tateia o armário escuro...) Só tem álbuns de fotos antigos e poeira. Nada de chaves aqui."
                        
                    elif perto_de_objeto == "gavetas" and historia_estado == "inicio":
                        texto_atual = "(Você puxa as gavetas com cuidado...) Tem alguns documentos antigos da casa e pilhas gastas. A chave não está aqui."
                        
                    elif perto_de_objeto == "sofa" and historia_estado == "inicio":
                        texto_atual = "(Você enfia as mãos sob as almofadas...) Só encontrei algumas moedas perdidas e um brinquedo quebrado de plástico. Nada."
                        
                    elif perto_de_objeto == "porta":
                        if tem_chave:
                            texto_atual = "(Você enfia a chave na fechadura trêmula e gira...) A porta real de madeira range e se abre! O vento frio da noite te abraça. Você conseguiu fugir! (Fim de Jogo)"
                            historia_estado = "fugiu"
                        elif historia_estado == "inicio":
                            texto_atual = "A porta está trancada por cima. Não adianta tentar forçar a maçaneta sem a chave certa."
            
    # Mecânica do Cronômetro Regressivo
    if historia_estado not in ["fugiu", "game_over"]:
        frames_contados += 1
        tempo_passado = frames_contados // 60
        tempo_restante = max(0, TEMPO_LIMITE_SEGUNDOS - tempo_passado)
        
        if tempo_restante <= 0:
            historia_estado = "game_over"
            texto_atual = "O tempo acabou. A porta do quarto bateu e os passos pesados do seu pai vieram em sua direção... Você foi pega."
    else:
        tempo_restante = 0
    
    # Atualização de Movimento do Jogador
    teclas = pygame.key.get_pressed()
    if historia_estado not in ["fugiu", "game_over"]:
        garota.update(teclas)

    # Detecção de proximidade com os móveis
    perto_de_objeto = None
    if garota.rect.colliderect(estante.rect): perto_de_objeto = "estante"
    elif garota.rect.colliderect(armario.rect): perto_de_objeto = "armario"
    elif garota.rect.colliderect(gavetas.rect): perto_de_objeto = "gavetas"
    elif garota.rect.colliderect(sofa.rect): perto_de_objeto = "sofa"
    elif garota.rect.colliderect(porta_saida.rect): perto_de_objeto = "porta"

    # --- SESSÃO DE RENDERIZAÇÃO E CAMADAS ---
    # Camada 1: Desenha o fundo da sala fotorrealista completo
    tela.blit(img_fundo, (0, 0))
    
    # Camada 2: Desenha todos os móveis e o sprite da garotinha por cima do fundo
