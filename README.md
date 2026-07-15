# B2B Sales Leads Generator
🔗 Живий застосунок: https://b2bsalesleads.streamlit.app/

Багатоагентний застосунок на Streamlit + CrewAI для генерації B2B-лідів через OpenRouter REST API.

## Опис
CrewAI-застосунок для генерації B2B Sales Leads з використанням багатоагентного підходу.

## Сценарій
Користувач вводить опис B2B-продукту, обирає модель та температуру, натискає кнопку запуску. 
CrewAI послідовно створює:
1. Портрет ідеального клієнта
2. Канали пошуку
3. Персоналізовані повідомлення
4. Критерії оцінювання
5. Фінальний план продажів

## Агенти
| Агент | Роль |
|-------|------|
| icp_researcher | Дослідник клієнтів |
| lead_planner | Фахівець із пошуку клієнтів |
| outreach_writer | Автор повідомлень |
| sales_reviewer | Фахівець з оцінювання клієнтів |

## Завдання
| Завдання | Агент | Контекст |
|----------|-------|----------|
| icp_task | icp_researcher | - |
| channels_task | lead_planner | icp_task |
| outreach_task | outreach_writer | icp_task, channels_task |
| qualification_task | sales_reviewer | icp_task, channels_task, outreach_task |
| final_task | icp_researcher | Всі попередні |

## Встановлення та запуск

### 1. Клонувати репозиторій
```bash
git clone <repository-url>
cd b2b-sales-crew