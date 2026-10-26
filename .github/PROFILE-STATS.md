# Ativar estatísticas privadas

O README começa com cards públicos de visualização. A primeira execução bem-sucedida de **Atualizar estatisticas do perfil** gera `profile/stats.svg` e `profile/top-langs.svg` com autenticação e passa o README a usar esses arquivos. As atualizações seguintes acontecem diariamente às 03:17 de São Paulo ou manualmente.

## Configuração

1. Aplique as alterações do pull request na branch `main`.
2. Em [Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens), crie um **token clássico** com prazo de expiração e escopos `repo` e `read:user`, conforme a [documentação da Action](https://github.com/stats-organization/github-readme-stats-action#inputs). O escopo `repo` é amplo: mantenha esse token exclusivamente em segredo. Se seus repositórios pertencem a uma organização, as políticas dela e a autorização SSO podem restringir o acesso.
3. Abra [os segredos de Actions deste repositório](https://github.com/FabricioSantossa/FabricioSantossa/settings/secrets/actions) e cadastre um **Repository secret** chamado `PROFILE_STATS_TOKEN`, cujo valor é o token. Não coloque o valor em arquivos, issues ou mensagens.
4. Na aba [Actions](https://github.com/FabricioSantossa/FabricioSantossa/actions), selecione **Atualizar estatisticas do perfil → Run workflow → main**. Confira se a execução fica verde e se os dois SVGs aparecem na pasta `profile`.
5. Para o calendário nativo, habilite também **Contribution settings → Private contributions** no seu perfil. Essa configuração é separada dos cards.

O token pessoal é usado para consultar as estatísticas; o `GITHUB_TOKEN` do workflow publica os arquivos neste repositório. O `GITHUB_TOKEN` sozinho não permite consultar todos os outros repositórios privados da conta. O token é fornecido à Action de geração de cards, cuja revisão está fixada no workflow.

## O que é contado

- O card mostra commits, estrelas, pull requests, issues, repositórios com contribuição, revisões e PRs mesclados, conforme os dados retornados pelo GitHub e as permissões do token.
- `include_all_commits=true` solicita o total histórico suportado pelo gerador. Não equivale a contar todo commit existente em qualquer branch. A atribuição à conta, o e-mail do autor e as regras do GitHub afetam o resultado.
- Os indicadores podem ter períodos diferentes. Revisões e repositórios com contribuição, por exemplo, seguem os períodos utilizados pelo gerador; não devem ser interpretados automaticamente como totais históricos.
- Linguagens medem a composição do código nos repositórios analisados. Não são horas de trabalho nem proficiência e não representam necessariamente todos os repositórios de organizações em que você contribui.
- Os SVGs publicados são públicos e podem incluir totais e composição de linguagens derivados de repositórios privados. Não publicam o código desses repositórios.
- A cobrinha continua usando o workflow existente e o calendário de contribuições; sua contagem é independente dos cards.

## Se falhar

- **Segredo ausente:** cadastre `PROFILE_STATS_TOKEN`. O workflow falha explicitamente para não apresentar dados públicos como privados.
- **Token expirado, revogado ou sem acesso:** substitua o segredo e confira permissões/SSO da organização.
- **Consulta ou geração falhou:** os cards anteriores ficam preservados; o workflow só faz commit após gerar ambos com sucesso.
- **Push negado:** confira regras de proteção de `main` e a permissão de escrita de Actions. Não desative regras de proteção; ajuste a publicação para respeitá-las.
- **Nenhuma mudança nos dados:** a execução termina com sucesso sem criar commit.

Referências: [GitHub Readme Stats Action](https://github.com/stats-organization/github-readme-stats-action), [contribuições no perfil](https://docs.github.com/en/account-and-profile/concepts/contributions-on-your-profile).
