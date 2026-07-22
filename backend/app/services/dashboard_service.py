from datetime import datetime, timedelta, timezone
from collections.abc import Iterable

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise as ExerciseModel
from app.models.class_enrollment import ClassEnrollment
from app.models.knowledge_component import KnowledgeComponent as KnowledgeComponentModel
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.models.user import User
from app.schemas.dashboard import (
    ClassDashboardSummary,
    ClassStudentActivity,
    ClassStudentDetailHeader,
    ClassStudentDetailResponse,
    ClassStudentDirectoryItem,
    ClassStudentDirectoryResponse,
    ClassHeatmapCell,
    DashboardResponse,
    DashboardTotals,
    Exercise,
    KnowledgeComponent,
    RecentSubmission,
    RiskStudent,
    WeakKcSummary,
)
from app.schemas.sessions import UserProfile
from app.services.exercise_service import to_frontend_status
from app.services.mastery_service import mastery_state
from app.services.recommendation_service import choose_recommended_exercise


# Build the dashboard response using the authenticated user and PostgreSQL data.
def build_dashboard_response(db: Session, current_user: UserProfile) -> DashboardResponse:
    kcs = list_dashboard_mastery(db, current_user.student_id)
    exercises = list_dashboard_exercises(db)
    mastery_average = round(sum(kc.mastery for kc in kcs) / len(kcs), 2) if kcs else 0.0
    recommended = choose_recommended_exercise(exercises)
    recommended_exercise_id = recommended.id if recommended is not None else ""
    active_goal = "Practice weak Python concepts"
    backend_status = "connected"
    learning_path = sorted(kcs, key=lambda kc: kc.mastery)[:5]

    return DashboardResponse(
        studentId=current_user.student_id,
        studentName=current_user.name,
        activeGoal=active_goal,
        backendStatus=backend_status,
        masteryAverage=mastery_average,
        recommendedExerciseId=recommended_exercise_id,
        recommendedExercise=recommended,
        masteryProfile=kcs,
        learningPath=learning_path,
    )


# Read the current student's KC mastery values from PostgreSQL.
def list_dashboard_mastery(db: Session, student_id: str) -> list[KnowledgeComponent]:
    rows = db.execute(
        select(
            KnowledgeComponentModel.id,
            KnowledgeComponentModel.name,
            KnowledgeComponentModel.short_name,
            KnowledgeComponentModel.description,
            StudentMastery.mastery,
        )
        .join(StudentMastery, StudentMastery.kc_id == KnowledgeComponentModel.id)
        .where(StudentMastery.student_id == student_id)
        .order_by(KnowledgeComponentModel.id)
    ).all()

    return [
        KnowledgeComponent(
            id=row.id,
            code=row.id,
            name=row.name,
            shortName=row.short_name,
            description=row.description or "",
            mastery=row.mastery,
            trend=0.0,
            state=mastery_state(row.mastery),
        )
        for row in rows
    ]


# Read exercise summaries from PostgreSQL for the dashboard queue.
def list_dashboard_exercises(db: Session) -> list[Exercise]:
    exercises = db.scalars(select(ExerciseModel).order_by(ExerciseModel.id)).all()

    return [
        Exercise(
            id=exercise.id,
            title=exercise.title,
            kc=exercise.kc_id,
            primaryKc=exercise.kc_id,
            difficulty=exercise.difficulty,
            estimatedMinutes=exercise.estimated_minutes,
            status=to_frontend_status(exercise.status),
        )
        for exercise in exercises
    ]


def build_class_dashboard_summary(db: Session, class_id: str) -> ClassDashboardSummary:
    users = db.scalars(
        select(User)
        .join(ClassEnrollment, ClassEnrollment.user_id == User.student_id)
        .where(ClassEnrollment.class_id == class_id)
        .where(User.is_active.is_(True))
        .where(User.role == "student")
        .order_by(User.student_id)
    ).all()
    kcs = db.scalars(select(KnowledgeComponentModel).order_by(KnowledgeComponentModel.id)).all()
    mastery_rows = db.scalars(select(StudentMastery)).all()
    mastery_by_student_kc = {
        (row.student_id, row.kc_id): row.mastery
        for row in mastery_rows
    }

    heatmap = [
        ClassHeatmapCell(
            student_id=user.student_id,
            display_name=user.name,
            kc_code=kc.id,
            kc_name=kc.name,
            kc_short_name=kc.short_name,
            mastery=mastery_by_student_kc.get((user.student_id, kc.id), 0.0),
        )
        for user in users
        for kc in kcs
    ]
    student_averages = {
        user.student_id: average(
            mastery_by_student_kc.get((user.student_id, kc.id), 0.0)
            for kc in kcs
        )
        for user in users
    }
    risk_students = build_risk_students(users, kcs, mastery_by_student_kc, student_averages)
    weak_kcs = build_weak_kcs(users, kcs, mastery_by_student_kc)
    student_ids = [user.student_id for user in users]
    recent_submissions = build_recent_submissions(db, student_ids=student_ids)
    submissions_7d = count_submissions_since(
        db,
        datetime.now(timezone.utc) - timedelta(days=7),
        student_ids=student_ids,
    )
    average_mastery = average(cell.mastery for cell in heatmap)

    updated_at = datetime.now(timezone.utc).isoformat()

    return ClassDashboardSummary(
        class_id=class_id,
        updated_at=updated_at,
        totals=DashboardTotals(
            students=len(users),
            average_mastery=round(average_mastery, 2),
            submissions_7d=submissions_7d,
            hint_requests_7d=0,
            at_risk_count=len(risk_students),
        ),
        heatmap=heatmap,
        risk_students=risk_students,
        weak_kcs=weak_kcs,
        recent_submissions=recent_submissions,
    )


def count_submissions_since(
    db: Session,
    since: datetime,
    student_ids: list[str] | None = None,
) -> int:
    statement = select(Submission.created_at)
    if student_ids is not None:
        statement = statement.where(Submission.student_id.in_(student_ids))
    rows = db.scalars(statement).all()
    threshold = normalise_datetime(since)

    return sum(1 for created_at in rows if normalise_datetime(created_at) >= threshold)


def build_recent_submissions(
    db: Session,
    limit: int = 10,
    student_ids: list[str] | None = None,
) -> list[RecentSubmission]:
    statement = (
        select(Submission, User.name, ExerciseModel.title, ExerciseModel.kc_id)
        .join(User, User.student_id == Submission.student_id)
        .join(ExerciseModel, ExerciseModel.id == Submission.exercise_id)
        .where(User.role == "student")
        .order_by(Submission.created_at.desc(), Submission.id.desc())
    )
    if student_ids is not None:
        if not student_ids:
            return []
        statement = statement.where(Submission.student_id.in_(student_ids))

    rows = db.execute(statement.limit(limit)).all()

    return [
        RecentSubmission(
            id=str(submission.id),
            student_id=submission.student_id,
            display_name=display_name,
            exercise_title=exercise_title,
            kc_code=kc_code,
            status=submission_status(submission),
            passed_count=count_passed_tests(submission.test_results),
            total_count=len(submission.test_results or []),
            runtime_ms=0,
            created_at=format_submission_time(submission.created_at),
        )
        for submission, display_name, exercise_title, kc_code in rows
    ]


def build_risk_students(
    users: list[User],
    kcs: list[KnowledgeComponentModel],
    mastery_by_student_kc: dict[tuple[str, str], float],
    student_averages: dict[str, float],
) -> list[RiskStudent]:
    risk_students: list[RiskStudent] = []

    for user in users:
        average_mastery = student_averages[user.student_id]

        if average_mastery >= 0.6:
            continue

        weakest_kc = min(
            kcs,
            key=lambda kc: mastery_by_student_kc.get((user.student_id, kc.id), 0.0),
            default=None,
        )

        risk_students.append(
            RiskStudent(
                student_id=user.student_id,
                display_name=user.name,
                average_mastery=round(average_mastery, 2),
                failed_attempts_7d=0,
                hints_used_7d=0,
                weakest_kc=weakest_kc.name if weakest_kc is not None else "No KC data",
                last_active_at="No recent activity",
            )
        )

    return sorted(risk_students, key=lambda student: student.average_mastery)


def build_weak_kcs(
    users: list[User],
    kcs: list[KnowledgeComponentModel],
    mastery_by_student_kc: dict[tuple[str, str], float],
) -> list[WeakKcSummary]:
    weak_kcs = [
        WeakKcSummary(
            kc_code=kc.id,
            kc_name=kc.name,
            average_mastery=round(
                average(mastery_by_student_kc.get((user.student_id, kc.id), 0.0) for user in users),
                2,
            ),
            affected_students=sum(
                1
                for user in users
                if mastery_by_student_kc.get((user.student_id, kc.id), 0.0) < 0.6
            ),
            trend=0.0,
        )
        for kc in kcs
    ]

    return sorted(weak_kcs, key=lambda kc: kc.average_mastery)


def average(values: Iterable[float]) -> float:
    items = list(values)

    if not items:
        return 0.0

    return sum(items) / len(items)


def count_passed_tests(test_results: list[dict] | None) -> int:
    return sum(1 for result in test_results or [] if result.get("passed") is True)


def submission_status(submission: Submission) -> str:
    if submission.passed:
        return "passed"

    if submission.status.lower() in {"error", "runtime error", "compilation error"}:
        return "error"

    return "failed"


def format_submission_time(created_at: datetime) -> str:
    normalised = normalise_datetime(created_at)
    return normalised.strftime("%d %b %H:%M")


def normalise_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def teacher_has_class_access(db: Session, teacher_id: str, class_id: str) -> bool:
    return db.get(ClassEnrollment, (class_id, teacher_id)) is not None


def list_class_students(
    db: Session,
    class_id: str,
    query: str = "",
    risk: str = "all",
    sort_by: str = "risk",
    limit: int = 20,
    offset: int = 0,
) -> ClassStudentDirectoryResponse:
    statement = (
        select(User)
        .join(ClassEnrollment, ClassEnrollment.user_id == User.student_id)
        .where(ClassEnrollment.class_id == class_id)
        .where(User.is_active.is_(True))
        .where(User.role == "student")
    )
    normalized_query = query.strip().lower()
    if normalized_query:
        pattern = f"%{normalized_query}%"
        statement = statement.where(
            or_(
                func.lower(User.name).like(pattern),
                func.lower(User.student_id).like(pattern),
            )
        )

    users = db.scalars(statement.order_by(User.name, User.student_id)).all()
    student_ids = [user.student_id for user in users]
    mastery_by_student = load_mastery_by_student(db, student_ids)
    last_active_by_student = load_last_active_by_student(db, student_ids)
    items = [
        build_directory_item(
            user,
            mastery_by_student.get(user.student_id, []),
            last_active_by_student.get(user.student_id),
        )
        for user in users
    ]

    if risk == "at_risk":
        items = [item for item in items if item.risk_level == "at_risk"]

    if sort_by == "name":
        items.sort(key=lambda item: (item.display_name.lower(), item.student_id))
    elif sort_by == "recent":
        items.sort(key=lambda item: item.last_active_at == "No recent activity")
    else:
        items.sort(key=lambda item: (item.average_mastery, item.display_name.lower()))

    total = len(items)
    page = items[offset : offset + limit]
    next_offset = offset + limit if offset + limit < total else None
    return ClassStudentDirectoryResponse(items=page, total=total, next_offset=next_offset)


def get_class_student_detail(
    db: Session,
    class_id: str,
    student_id: str,
) -> ClassStudentDetailResponse | None:
    user = db.scalar(
        select(User)
        .join(ClassEnrollment, ClassEnrollment.user_id == User.student_id)
        .where(ClassEnrollment.class_id == class_id)
        .where(User.student_id == student_id)
        .where(User.is_active.is_(True))
        .where(User.role == "student")
    )
    if user is None:
        return None

    mastery_profile = list_dashboard_mastery(db, student_id)
    last_active = load_last_active_by_student(db, [student_id]).get(student_id)
    directory_item = build_directory_item(user, mastery_profile, last_active)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    submissions = db.scalars(
        select(Submission).where(Submission.student_id == student_id)
    ).all()
    recent_submissions = build_recent_submissions(db, student_ids=[student_id])
    submissions_7d = sum(
        1 for submission in submissions if normalise_datetime(submission.created_at) >= seven_days_ago
    )
    failed_attempts_7d = sum(
        1
        for submission in submissions
        if normalise_datetime(submission.created_at) >= seven_days_ago and not submission.passed
    )

    return ClassStudentDetailResponse(
        student=ClassStudentDetailHeader(
            student_id=directory_item.student_id,
            display_name=directory_item.display_name,
            average_mastery=directory_item.average_mastery,
            risk_level=directory_item.risk_level,
            last_active_at=directory_item.last_active_at,
        ),
        mastery_profile=mastery_profile,
        weak_kcs=sorted(mastery_profile, key=lambda item: item.mastery)[:3],
        activity=ClassStudentActivity(
            submissions_7d=submissions_7d,
            failed_attempts_7d=failed_attempts_7d,
            hints_used_7d=0,
            recent_submissions=recent_submissions,
        ),
    )


def load_mastery_by_student(
    db: Session,
    student_ids: list[str],
) -> dict[str, list[KnowledgeComponent]]:
    profiles = {student_id: [] for student_id in student_ids}
    if not student_ids:
        return profiles

    rows = db.execute(
        select(
            StudentMastery.student_id,
            KnowledgeComponentModel.id,
            KnowledgeComponentModel.name,
            KnowledgeComponentModel.short_name,
            KnowledgeComponentModel.description,
            StudentMastery.mastery,
        )
        .join(KnowledgeComponentModel, KnowledgeComponentModel.id == StudentMastery.kc_id)
        .where(StudentMastery.student_id.in_(student_ids))
        .order_by(StudentMastery.student_id, KnowledgeComponentModel.id)
    ).all()

    for row in rows:
        profiles[row.student_id].append(
            KnowledgeComponent(
                id=row.id,
                code=row.id,
                name=row.name,
                shortName=row.short_name,
                description=row.description or "",
                mastery=row.mastery,
                trend=0.0,
                state=mastery_state(row.mastery),
            )
        )

    return profiles


def load_last_active_by_student(
    db: Session,
    student_ids: list[str],
) -> dict[str, datetime]:
    if not student_ids:
        return {}
    rows = db.execute(
        select(Submission.student_id, func.max(Submission.created_at))
        .where(Submission.student_id.in_(student_ids))
        .group_by(Submission.student_id)
    ).all()
    return {student_id: created_at for student_id, created_at in rows if created_at is not None}


def build_directory_item(
    user: User,
    mastery_profile: list[KnowledgeComponent],
    last_active_at: datetime | None,
) -> ClassStudentDirectoryItem:
    average_mastery = average(item.mastery for item in mastery_profile)
    weakest = min(mastery_profile, key=lambda item: item.mastery, default=None)
    return ClassStudentDirectoryItem(
        student_id=user.student_id,
        display_name=user.name,
        average_mastery=round(average_mastery, 2),
        risk_level="at_risk" if average_mastery < 0.6 else "on_track",
        weakest_kc=weakest.name if weakest is not None else "No KC data",
        last_active_at=(
            format_submission_time(last_active_at)
            if last_active_at is not None
            else "No recent activity"
        ),
    )
