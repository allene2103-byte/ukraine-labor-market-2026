from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

root = Path(__file__).resolve().parent
charts = root / "charts"
charts.mkdir(exist_ok=True)
df = pd.read_csv(root / "data" / "professions.csv", dtype={"code": str})

# Для порівняння конкуренції обидва показники беруться на одну дату.
# Поріг у 100 вакансій зменшує вплив малих знаменників.
eligible = df.loc[df["vacancies_oct_1"] >= 100].copy()
eligible["jobseekers_per_vacancy"] = (
    eligible["jobseekers_oct_1"] / eligible["vacancies_oct_1"]
)
top_demand = df.nlargest(10, "vacancies_jan_sep")
top_competition = eligible.nlargest(10, "jobseekers_per_vacancy")

print(f"Рядків у наборі: {len(df)}")
print(df[["vacancies_jan_sep", "vacancies_oct_1", "jobseekers_oct_1"]].sum())
print(f"Професій із щонайменше 100 вакансіями: {len(eligible)}")
print(top_demand[["profession", "vacancies_jan_sep"]].to_string(index=False))
print(top_competition[["profession", "jobseekers_per_vacancy"]].round(2).to_string(index=False))
print(eligible.nsmallest(5, "jobseekers_per_vacancy")[["profession", "jobseekers_per_vacancy"]].round(2).to_string(index=False))

for table, column, title, xlabel, filename in [
    (top_demand, "vacancies_jan_sep", "Топ-10 професій за кількістю вакансій",
     "Вакансії за січень–вересень 2026 року", "top_vacancies.png"),
    (top_competition, "jobseekers_per_vacancy", "Де найбільше шукачів на вакансію",
     "Шукачів на вакансію на 1 жовтня 2026 року (від 100 вакансій)", "competition.png"),
]:
    fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")
    plot = table.iloc[::-1]
    bars = ax.barh(plot["profession"], plot[column], color="#236b83")
    ax.bar_label(bars, fmt="%.2f" if column == "jobseekers_per_vacancy" else "%.0f", padding=4)
    ax.margins(x=0.16)
    ax.set(title=title, xlabel=xlabel)
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    fig.savefig(charts / filename, dpi=150)
    plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 6), layout="constrained")
ax.scatter(eligible["vacancies_oct_1"], eligible["jobseekers_oct_1"],
           alpha=0.65, color="#236b83")
limit = max(eligible["vacancies_oct_1"].max(), eligible["jobseekers_oct_1"].max())
ax.plot([0, limit], [0, limit], "--", color="#a34d24", label="Один шукач на вакансію")
ax.set(xlim=(0, eligible["vacancies_oct_1"].max() * 1.08),
       title="Вакансії та шукачі за професіями на 1 жовтня 2026 року",
       xlabel="Відкриті вакансії (професії з ≥ 100 вакансіями)",
       ylabel="Зареєстровані шукачі")
ax.legend()
ax.grid(alpha=0.2)
fig.savefig(charts / "vacancies_vs_jobseekers.png", dpi=150)
plt.close(fig)
