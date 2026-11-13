"""Render the studio's source-backed loyalty offer, review cards and visible FAQ."""
from html import escape as H

ARROW = '<svg class="icon" aria-hidden="true"><use href="#arrow-up"/></svg>'


def procedure_details(kind):
    if kind == 'spa':
        return '''<ul class="procedure-points">
          <li><strong>Увлажнить кожу.</strong> В уход входит увлажняющий тоник на основе гидролата розы.</li>
          <li><strong>Освежить тон лица.</strong> LED-маска дополняет уход за кожей, которая выглядит тусклой.</li>
          <li><strong>Дать себе передышку.</strong> Пока идёт процедура, можно удобно устроиться на кушетке и немного выдохнуть.</li>
        </ul><p class="care-note">Если кожа чувствительна к свету или вы принимаете лекарства, расскажите об этом специалисту до сеанса.</p>'''
    if kind == 'body':
        return '''<ul class="procedure-points">
          <li><strong>Кому подходит.</strong> Охлаждение используют для небольших участков подкожного жира, например на животе или боках. Для снижения веса и при ожирении метод не подходит.</li>
          <li><strong>Что вы почувствуете.</strong> В первые минуты возможны сильный холод, натяжение или покалывание. По мере охлаждения эти ощущения обычно ослабевают. Если вам больно, скажите об этом сразу.</li>
          <li><strong>С чего начать.</strong> На консультации можно спокойно обсудить, подойдёт ли вам процедура, какие изменения возможны и чего ждать после сеанса.</li>
        </ul><details class="care-more"><summary>Противопоказания и возможные реакции</summary>
          <p>Расскажите специалисту, если у вас бывает крапивница от холода или есть грыжа в зоне воздействия. При этих состояниях процедуру не проводят.</p>
          <p>После сеанса возможны покраснение, отёк, синяки или онемение. Среди более редких осложнений бывают холодовой ожог и увеличение жировой ткани в обработанной зоне. В последнем случае может потребоваться операция.</p>
          <a class="text-link" href="https://www.fda.gov/medical-devices/aesthetic-cosmetic-devices/non-invasive-body-contouring-technologies" target="_blank" rel="noopener noreferrer">О методе и рисках на сайте FDA ↗</a>
        </details>'''
    return ''


def loyalty_copy(data):
    return f'''<div class="app-copy"><p class="eyebrow">ПРИЛОЖЕНИЕ СТУДИИ</p><h2 id="application-title">Про НЕЁ.<br><em>Всегда рядом.</em></h2><p class="app-lead">Любимая студия в одно касание.</p><div class="app-benefits"><span><svg class="icon"><use href="#spark"/></svg> Запись в удобное время</span><span><svg class="icon"><use href="#spark"/></svg> Чат со студией</span><span><svg class="icon"><use href="#spark"/></svg> Бонусы и привилегии</span><span><svg class="icon"><use href="#spark"/></svg> Работа без VPN</span></div></div>'''


def loyalty_banner(data):
    return f'''<section class="section container loyalty-section" id="loyalty" aria-labelledby="loyalty-title"><div class="loyalty-panel"><div class="loyalty-offer"><p class="eyebrow">ПРИВЕТСТВЕННЫЕ БОНУСЫ</p><h2 id="loyalty-title">Забери свои<br><em>2 000 ₽</em><span>бонусами</span></h2></div><div class="loyalty-panel-copy"><h3>Скачай приложение.<br>Напиши «Хочу бонусы».</h3><p>Присоединяйся к нашей программе лояльности.</p><ul class="loyalty-perks"><li>Получай кэшбэк</li><li>Списывай бонусы</li><li>Делись с хорошими друзьями</li></ul><a class="button loyalty-button" href="{H(data['download_url'], quote=True)}" data-download aria-haspopup="dialog" aria-controls="download-dialog">Хочу бонус {ARROW}</a><p class="loyalty-short-terms">Первым 20 новым пользователям.<br>До 50% оплаты бонусами. Срок действия: 2 месяца.</p><details class="loyalty-terms"><summary>Все условия предложения</summary><p>{H(data['terms'])}</p></details></div></div></section>'''


def review_cards(data):
    cards = []
    for item in data['items']:
        initials = ''.join(w[0] for w in item['author'].split()[:2])
        stars = '<span aria-hidden="true">' + '★' * item['rating'] + '</span>'
        cards.append(f'''<article class="review-excerpt"><header class="review-excerpt-head"><span class="review-avatar" aria-hidden="true">{H(initials)}</span><div><p class="review-author-name">{H(item['author'])}</p><p class="review-date"><time datetime="{item['published_at']}">{H(item['date_label'])}</time></p></div><a class="review-provider" href="{H(item['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">{H(item['source_name'])}</a></header><div class="review-stars" aria-label="Оценка {item['rating']} из 5">{stars}</div><blockquote><p>«{H(item['quote'])}»</p></blockquote><a class="review-read-link" href="{H(item['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Читать на {H(item.get('read_label',item['source_name']))} ↗</a><p class="review-excerpt-note">Фрагмент отзыва</p></article>''')
    dikidi=data['dikidi']
    return f'''<section class="section reviews-section" id="reviews" aria-labelledby="reviews-title"><div class="container"><div class="section-heading reviews-heading"><h2 id="reviews-title">Отзывы клиентов.</h2></div><div class="review-platforms"><div class="review-source-card"><div><h3>Яндекс Карты</h3><iframe class="yandex-rating-badge" title="Рейтинг Про НЕЁ на Яндекс Картах" src="{H(data['rating_widget_url'], quote=True)}" width="150" height="50" loading="lazy"></iframe></div><a class="source-platform-action" href="{H(data['source'], quote=True)}" target="_blank" rel="noopener noreferrer">Открыть отзывы {ARROW}</a></div><div class="review-source-card"><div><h3>DIKIDI</h3><div class="dikidi-rating"><strong>{H(dikidi['rating_label'])}</strong><span class="review-stars" aria-hidden="true">★★★★★</span></div><p class="source-review-count">{H(dikidi['count_label'])}</p></div><a class="source-platform-action" href="{H(dikidi['url'], quote=True)}" target="_blank" rel="noopener noreferrer">Открыть отзывы {ARROW}</a></div></div><div class="reviews-grid">{''.join(cards)}</div></div></section>'''


def faq_section(items):
    rows = []
    for item in items:
        link = item.get('link')
        extra = f' <a class="text-link" href="{H(link["url"], quote=True)}">{H(link["label"])}</a>' if link else ''
        rows.append(f'<details class="faq-item"><summary><h3>{H(item["question"])}</h3><span aria-hidden="true">+</span></summary><div class="faq-answer"><p>{H(item["answer"])}</p>{extra}</div></details>')
    return '<section class="section container faq-section" id="faq" aria-labelledby="faq-title"><div class="faq-heading"><p class="eyebrow">FAQ</p><h2 id="faq-title">Частые вопросы.</h2></div><div class="faq-list">' + ''.join(rows) + '</div></section>'


def faq_schema(items, base):
    return {'@type': 'FAQPage', '@id': base + '/#faq', 'isPartOf': {'@id': base + '/#webpage'},
            'mainEntity': [{'@type': 'Question', 'name': row['question'],
                            'acceptedAnswer': {'@type': 'Answer', 'text': row['answer']}} for row in items]}
