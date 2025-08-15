from src.models.pet import Pet, db

def init_pets():
    """Inicializa todos os pets no banco de dados"""
    
    # Verificar se os pets já foram inicializados
    if Pet.query.count() > 0:
        print("Pets já inicializados, pulando...")
        return
    
    pets_data = [
        # Pets Comuns
        {
            'name': 'Esquilo Saltitante',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_esquilo.png',
            'base_effects': {'coin_bonus': 0.03}
        },
        {
            'name': 'Panda de Bambu',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_panda.png',
            'base_effects': {'xp_bonus': 0.03}
        },
        {
            'name': 'Pinguim Desajeitado',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_pinguim.png',
            'base_effects': {'easy_task_xp_bonus': 0.05}
        },
        {
            'name': 'Tartaruga Forte',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_tartaruga.png',
            'base_effects': {'hard_task_coin_bonus': 0.05}
        },
        {
            'name': 'Sapo Curioso',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_sapo.png',
            'base_effects': {'first_task_coin_bonus': 10}
        },
        {
            'name': 'Coelho Veloz',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_coelho.png',
            'base_effects': {'xp_bonus': 0.02, 'coin_bonus': 0.02}
        },
        {
            'name': 'Rato Engenhoso',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_rato.png',
            'base_effects': {'last_task_xp_bonus': 0.05}
        },
        {
            'name': 'Gato Preto da Sorte',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_gato_preto.png',
            'base_effects': {'lucky_chance_coin_bonus': 0.02}
        },
        {
            'name': 'Coruja Sábia',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_coruja.png',
            'base_effects': {'xp_bonus': 0.07}
        },
        {
            'name': 'Cão Leal',
            'rarity': 'common',
            'sprite_path': '/sprites/pet_comum_cao.png',
            'base_effects': {'coin_bonus': 0.07}
        },
        
        # Pets Raros
        {
            'name': 'Grifo Veloz',
            'rarity': 'rare',
            'sprite_path': '/sprites/pet_raro_grifo.png',
            'base_effects': {'instant_task_chance': 0.05}
        },
        {
            'name': 'Golem de Cristal',
            'rarity': 'rare',
            'sprite_path': '/sprites/pet_raro_golem.png',
            'base_effects': {'store_discount': 0.10}
        },
        {
            'name': 'Gato da Sorte',
            'rarity': 'rare',
            'sprite_path': '/sprites/pet_raro_gato_sorte.png',
            'base_effects': {'duplicate_coin_chance': 0.05}
        },
        {
            'name': 'Dragão Bebê',
            'rarity': 'rare',
            'sprite_path': '/sprites/pet_raro_dragao_bebe.png',
            'base_effects': {'xp_bonus': 0.10, 'coin_bonus': 0.10}
        },
        {
            'name': 'Fada da Floresta',
            'rarity': 'rare',
            'sprite_path': '/sprites/pet_raro_fada.png',
            'base_effects': {'streak_protection_chance': 0.01, 'xp_bonus': 0.05}
        },
        {
            'name': 'Unicórnio Místico',
            'rarity': 'rare',
            'sprite_path': '/sprites/pet_raro_unicornio.png',
            'base_effects': {'xp_bonus': 0.08, 'coin_bonus': 0.08}
        },
        
        # Pets Épicos
        {
            'name': 'Dragão das Sombras',
            'rarity': 'epic',
            'sprite_path': '/sprites/pet_epico_dragao_sombrio.png',
            'base_effects': {'weekend_xp_bonus': 0.15, 'weekend_coin_bonus': 0.15}
        },
        {
            'name': 'Lobo Espectral',
            'rarity': 'epic',
            'sprite_path': '/sprites/pet_epico_lobo_espectral.png',
            'base_effects': {'weekday_xp_bonus': 0.15, 'weekday_coin_bonus': 0.15}
        },
        {
            'name': 'Fênix de Fogo',
            'rarity': 'epic',
            'sprite_path': '/sprites/pet_epico_fenix_fogo.png',
            'base_effects': {'revive_streak_chance': 0.01, 'xp_bonus': 0.10}
        },
        
        # Pets Lendários
        {
            'name': 'Dragão Dourado',
            'rarity': 'legendary',
            'sprite_path': '/sprites/pet_lendario_dragao_dourado.png',
            'base_effects': {'xp_bonus': 0.20, 'coin_bonus': 0.20, 'all_task_bonus': 0.05}
        },
        {
            'name': 'Fênix Dourada',
            'rarity': 'legendary',
            'sprite_path': '/sprites/pet_lendario_fenix_dourada.png',
            'base_effects': {'streak_protection_chance': 0.05, 'xp_bonus': 0.10, 'coin_bonus': 0.10}
        }
    ]
    
    # Verificar se os pets já existem
    existing_pets = Pet.query.count()
    if existing_pets > 0:
        print(f"Pets já inicializados ({existing_pets} pets encontrados)")
        return
    
    # Criar pets
    for pet_data in pets_data:
        pet = Pet(**pet_data)
        db.session.add(pet)
    
    db.session.commit()
    print(f"Inicializados {len(pets_data)} pets no banco de dados")

if __name__ == '__main__':
    from src.main import app
    with app.app_context():
        init_pets()

