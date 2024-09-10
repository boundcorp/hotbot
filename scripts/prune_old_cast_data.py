def run(days=3):
    from hotbot.apps.farcaster.models import Cast
    from django.utils import timezone
    from datetime import timedelta
    from django.db import connection

    # Delete old records
    deleted_count = Cast.objects.filter(created_at__lt=timezone.now() - timedelta(days=int(days))).delete()[0]
    print(f"Deleted {deleted_count} old Cast records")

    # Reclaim space using PostgreSQL-specific commands
    with connection.cursor() as cursor:
        cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"Reclaiming space for table: {table_name}")
            cursor.execute(f"VACUUM FULL {table_name};")
            cursor.execute(f"REINDEX TABLE {table_name};")

    print("Space reclamation complete")

