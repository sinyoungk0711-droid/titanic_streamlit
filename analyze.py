"""승객 CSV에서 대시보드와 챗봇이 함께 쓸 집계 데이터를 만든다."""
import csv
import pickle
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PKL = ROOT / "titanic_summary.pkl"


def summarize(rows):
    passengers = len(rows)
    survivors = sum(int(row["survived"]) for row in rows)
    return {
        "탑승자": passengers,
        "생존자": survivors,
        "생존율(%)": round(survivors / passengers * 100, 2),
    }


def group_summary(rows, column, labels):
    table = []
    for value, label in labels.items():
        group = [row for row in rows if row[column] == value]
        if group:
            table.append({"그룹": label, **summarize(group)})
    return table


def group_fact(table):
    return " / ".join(
        f"{row['그룹']} {row['생존율(%)']:.2f}%"
        f"({row['생존자']}/{row['탑승자']}명)"
        for row in table
    )


def analyze(rows):
    total = summarize(rows)
    by_sex = group_summary(rows, "sex", {"female": "여성", "male": "남성"})
    by_class = group_summary(
        rows, "pclass", {"1": "1등급", "2": "2등급", "3": "3등급"}
    )
    missing_age = sum(not row["age"].strip() for row in rows)
    ports = sorted({row["embark_town"] for row in rows if row["embark_town"]})
    facts = [
        ("F-1", "전체 생존 현황",
         f"전체 {total['탑승자']}명 중 {total['생존자']}명이 생존했다. "
         f"생존율은 {total['생존율(%)']:.2f}%이고 "
         f"사망자는 {total['탑승자'] - total['생존자']}명이다."),
        ("F-2", "성별 생존 현황", group_fact(by_sex)),
        ("F-3", "객실 등급별 생존 현황", group_fact(by_class)),
        ("F-4", "나이 결측치", f"나이가 기록되지 않은 승객은 {missing_age}명이다."),
        ("F-5", "승선 도시", f"기록된 승선 도시는 {len(ports)}곳이다. {', '.join(ports)}."),
    ]
    return {
        "total": total,
        "by_sex": by_sex,
        "by_class": by_class,
        "missing_age": missing_age,
        "facts": facts,
    }


def main():
    with (ROOT / "titanic.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    summary = analyze(rows)
    with PKL.open("wb") as file:
        pickle.dump(summary, file)
    lines = ["# 타이타닉 사실표", "", "| 사실 ID | 주제 | 근거 |", "| --- | --- | --- |"]
    lines.extend(f"| {fact_id} | {topic} | {evidence} |"
                 for fact_id, topic, evidence in summary["facts"])
    (ROOT / "titanic_facts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Created titanic_summary.pkl and titanic_facts.md")


if __name__ == "__main__":
    main()
