"""Render the studio's source-backed loyalty offer, review cards and visible FAQ."""
from html import escape as H

ARROW = '<svg class="icon" aria-hidden="true"><use href="#arrow-up"/></svg>'


def loyalty_copy(data):
    return f'''<div class="app-copy loyalty-copy"><p class="eyebrow">ПРОГРАММА ЛОЯЛЬНОСТИ</p><h2 id="application-title">Забери свои<br><em><span class="loyalty-amount">2 000 ₽</span> бонусами.</em></h2><p class="app-lead">Присоединяйся к «Про НЕЁ» в приложении.</p><ul class="loyalty-benefits"><li>Получай кэшбэк бонусами</li><li>Списывай бонусы на услуги</li><li>Делись с хорошими друзьями</li></ul><a class="button" href="{H(data['download_url'], quote=True)}" data-download aria-haspopup="dialog" aria-controls="download-dialog">Хочу бонус {ARROW}</a><p class="loyalty-instruction">Скачай приложение и напиши в чате<br>«Хочу бонусы».</p><details class="loyalty-terms"><summary>Условия бонусного предложения</summary><p>{H(data['terms'])}</p></details></div>'''


def review_cards(data):
    cards = []
    for item in data['items']:
        initials = ''.join(w[0] for w in item['author'].split()[:2])
        stars = '<span aria-hidden="true">' + '★' * item['rating'] + '</span>'
        cards.append(f'''<article class="yandex-review"><header class="yandex-review-head"><span class="yandex-avatar" aria-hidden="true">{H(initials)}</span><div><p class="yandex-author">{H(item['author'])}</p><p class="yandex-review-date"><time datetime="{item['published_at']}">{H(item['date_label'])}</time></p></div><a class="yandex-mark" href="{H(item['source_url'], quote=True)}" aria-label="Отзыв на Яндекс Картах" target="_blank" rel="noopener noreferrer">Я</a></header><div class="yandex-stars" aria-label="Оценка {item['rating']} из 5">{stars}</div><blockquote><p>«{H(item['quote'])}»</p></blockquote><a class="yandex-review-link" href="{H(item['source_url'], quote=True)}" target="_blank" rel="noopener noreferrer">Читать отзыв на Яндекс Картах ↗</a><p class="yandex-excerpt-note">Фрагмент отзыва</p></article>''')
    return f'''<section class="section reviews-section" id="reviews" aria-labelledby="reviews-title"><div class="container"><div class="section-heading reviews-heading"><h2 id="reviews-title">Отзывы клиентов.</h2><div class="yandex-rating-link"><iframe class="yandex-rating-badge" title="Рейтинг Про НЕЁ на Яндекс Картах" src="{H(data['rating_widget_url'], quote=True)}" width="150" height="50" loading="lazy"></iframe><a href="{H(data['source'], quote=True)}" target="_blank" rel="noopener noreferrer">Все отзывы на Яндекс Картах ↗</a></div></div><div class="reviews-grid">{''.join(cards)}</div></div></section>'''


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
