source .env
echo $PG_CONN_STR
psql ${PG_CONN_STR} -f create-table.sql