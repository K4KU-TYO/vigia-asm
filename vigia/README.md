# VIGIA

![Versão](https://img.shields.io/badge/versão-1.0.0-ffb000)
![Licença](https://img.shields.io/badge/licença-MIT-ffb000)
![Python](https://img.shields.io/badge/python-3.12+-ffb000)
![Status](https://img.shields.io/badge/status-ativo-39ff6a)

**A maioria das ferramentas de recon tira uma foto do alvo. O VIGIA fica de olho.**

Cadastre um domínio e o VIGIA passa a vigiá-lo continuamente: subdomínios, portas abertas e hosts HTTP são reescaneados automaticamente no intervalo que você definir. Quando algo muda — um painel admin que subiu, uma porta de banco de dados que abriu, um subdomínio de staging esquecido — ele calcula o diff contra o scan anterior e te avisa na hora, direto no Discord, Slack ou Telegram.

Sem depender de binários externos (nada de instalar subfinder/amass/nmap à parte), sem dashboard pago, sem vendor lock-in: é só Python, roda em qualquer lugar com um `docker compose up`.

> ⚠️ **Uso responsável**: escaneie apenas domínios que você possui ou tem autorização explícita para testar (programas de bug bounty, contratos de pentest, ativos próprios). Ver seção [Aviso legal](#aviso-legal).

---

**Sentinela de Superfície de Ataque** — monitoramento contínuo de OSINT/ASM (Attack Surface Management), com detecção de mudanças e alertas automáticos.

> Cadastre um domínio, e o VIGIA escaneia periodicamente, compara com o scan anterior e te avisa quando algo novo aparecer: um subdomínio, uma porta aberta, um host HTTP novo.

## Por que

Ferramentas de recon tradicionais fazem um scan pontual. Na prática, a superfície de ataque de um alvo muda o tempo todo — e é exatamente essa mudança que costuma valer a pena (um subdomínio de staging esquecido, um painel admin que subiu, uma porta que abriu). O VIGIA existe pra cobrir esse gap: reconhecimento **contínuo**, com **diff automático** e **alerta** quando importa.

## Funcionalidades

- Cadastro de múltiplos alvos, cada um com seu próprio intervalo de re-scan
- Reconhecimento sem dependências externas (só Python): subdomínios via certificate transparency (crt.sh) + brute force DNS, varredura de portas TCP comuns, probe HTTP/HTTPS com título e servidor
- Motor de diff: classifica cada ativo como **NOVO**, **REMOVIDO** ou **INALTERADO** frente ao scan anterior
- Alertas via webhook (Discord, Slack, Telegram) quando há mudanças
- Interface web própria, estilo terminal
- Agendamento automático em background (não depende de cron do SO)

## Arquitetura

O código segue princípios SOLID e é organizado em camadas bem separadas:

```
app/
├── models/          # Entidades (Alvo, Scan, Ativo) via SQLAlchemy
├── scanners/         # Um scanner por responsabilidade (Strategy Pattern)
│   ├── base.py         # contrato comum (Scanner)
│   ├── subdominio.py
│   ├── portas.py
│   └── http_probe.py
├── repositories/     # Acesso a dados isolado (Repository Pattern)
├── services/         # Regras de negócio (orquestração, diff, alertas)
├── notifiers/        # Um notificador por canal (Strategy Pattern)
├── routers/          # Rotas HTTP (FastAPI)
├── scheduler.py       # Agendador de scans automáticos
├── fabrica.py          # Injeção de dependências centralizada
└── static/            # Interface web (HTML/CSS/JS puro)
```

Adicionar um scanner novo (ex: verificação de tecnologias JS) ou um canal de notificação novo (ex: e-mail) não exige tocar em código existente — só criar uma nova classe que implementa a interface (`Scanner` ou `Notificador`) e registrá-la em `fabrica.py`.

## Como rodar

### Com Docker (recomendado)

```bash
cp .env.example .env
# edite o .env se quiser configurar webhooks de alerta
docker compose up --build
```

Acesse `http://localhost:8000`.

### Sem Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Configurando alertas

No `.env`, preencha qualquer combinação:

```bash
WEBHOOK_DISCORD=https://discord.com/api/webhooks/...
WEBHOOK_SLACK=https://hooks.slack.com/services/...
TELEGRAM_TOKEN=123456:ABC-seu-token
TELEGRAM_CHAT_ID=123456789
```

## Aviso legal

Use o VIGIA **apenas contra domínios que você possui ou tem autorização explícita para testar** (programas de bug bounty, pentests contratados, ativos da sua própria empresa). Escanear infraestrutura de terceiros sem autorização pode ser crime, dependendo da jurisdição. Os mantenedores não se responsabilizam pelo uso indevido da ferramenta.

## Versão

**v1.0.0** — versão inicial

- Cadastro de alvos com intervalo de re-scan configurável
- Scanners: subdomínios (crt.sh + brute force DNS), portas TCP comuns, probe HTTP/HTTPS
- Motor de diff (NOVO / REMOVIDO / INALTERADO) entre scans consecutivos
- Alertas via Discord, Slack e Telegram
- Agendador automático em background
- Interface web própria e CI básico no GitHub Actions

O versionamento segue [SemVer](https://semver.org/lang/pt-BR/): `MAJOR.MINOR.PATCH`.

## Roadmap / possíveis atualizações

Ideias para próximas versões — contribuições são bem-vindas em qualquer uma delas:

- [ ] **Fingerprint de tecnologia** — identificar CMS, frameworks e libs JS por host (novo `Scanner`, sem alterar o resto do código)
- [ ] **Certificados TLS ao vivo** — capturar validade, emissor e SANs direto via `ssl`, não só pelo crt.sh
- [ ] **Notificador por e-mail** — novo `Notificador` (SMTP) seguindo a mesma interface dos atuais
- [ ] **Wordlist customizável por alvo** — hoje é fixa; permitir upload de wordlist própria via interface
- [ ] **Exportação de relatórios** — gerar PDF/CSV do histórico de mudanças de um alvo
- [ ] **Autenticação multi-usuário** — hoje é single-user/self-hosted; adicionar login e permissões por equipe
- [ ] **Suporte a Postgres** — hoje SQLite por padrão; documentar/testar uso com Postgres em produção
- [ ] **Rate limiting configurável** — controle mais fino de agressividade do scan (útil pra programas de bug bounty com regras estritas)
- [ ] **Testes automatizados (pytest)** — cobertura de unidade pros services e scanners, integrado ao CI

Quer sugerir algo que não está na lista? Abra uma *issue* no repositório.

## Contribuindo

Pull requests são bem-vindos. O workflow de CI (`.github/workflows/ci.yml`) roda automaticamente em todo push/PR pra `main`, checando sintaxe e se a aplicação sobe corretamente.

## Licença

MIT — veja [LICENSE](LICENSE).
