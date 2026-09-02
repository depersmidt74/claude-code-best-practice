#!/usr/bin/env bash
# Самопроверка цепочки Binance → fmt24h.py.
#
#   bash scripts/test-fmt24h.sh
#
# Офлайн-проверки идут всегда. Сетевые выполняются, только если Binance
# отвечает; иначе они помечаются SKIP, и итог честно говорит, что цепочка
# целиком не подтверждена.
#
# Код выхода: 0 — все выполненные проверки прошли, 1 — есть провалы.

set -u
cd "$(dirname "$0")/.." || exit 1
FMT="scripts/fmt24h.py"
API="https://api.binance.com/api/v3/ticker/24hr"
pass=0; fail=0; skip=0

ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$1"; pass=$((pass+1)); }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n%s\n' "$1" "${2:+        → $2}"; fail=$((fail+1)); }
miss() { printf '  \033[33mSKIP\033[0m  %s — %s\n' "$1" "$2"; skip=$((skip+1)); }

# Ожидаемый код выхода + подстрока в выводе.
check() { # имя, ожидаемый_код, ожидаемая_подстрока, вход
  local name=$1 want=$2 needle=$3 input=$4 out code
  out=$(printf '%s' "$input" | python3 "$FMT" 2>&1); code=$?
  if [ "$code" -ne "$want" ]; then
    bad "$name" "код $code вместо $want; вывод: $(printf '%s' "$out" | head -1)"
  elif [ -n "$needle" ] && ! printf '%s' "$out" | grep -qF "$needle"; then
    bad "$name" "в выводе нет «$needle»: $(printf '%s' "$out" | head -1)"
  else
    ok "$name"
  fi
}

echo "Окружение"
command -v python3 >/dev/null && ok "python3 доступен" || bad "python3 доступен"
[ -f "$FMT" ] && ok "$FMT на месте" || { bad "$FMT на месте"; exit 1; }
command -v curl >/dev/null && ok "curl доступен" || bad "curl доступен"

echo
echo "Разбор ответов (без сети)"
check "список тикеров → таблица" 0 "СИМВОЛ" \
  '[{"symbol":"BTCUSDT","lastPrice":"79412.31","priceChangePercent":"-2.18","highPrice":"81990.0","lowPrice":"78650.12","quoteVolume":"4182338111.9","closeTime":1788377000000}]'
check "одиночный объект принимается" 0 "ETHUSDT" \
  '{"symbol":"ETHUSDT","lastPrice":"2611.45","priceChangePercent":"1.08","highPrice":"2664.0","lowPrice":"2570.31","quoteVolume":"1904221733.4","closeTime":1788377000000}'
check "ошибка биржи → код 1 и её текст" 1 "Invalid symbol" \
  '{"code":-1121,"msg":"Invalid symbol."}'
check "пустой список → код 2" 2 "Ответ пуст" '[]'
check "не JSON → код 2" 2 "не является JSON" '<html>502 Bad Gateway</html>'
check "пустой ввод → код 2" 2 "Пустой ввод" ''

echo
echo "Сеть"
if ! curl -sS --max-time 15 -o /dev/null "$API?symbol=BTCUSDT" 2>/dev/null; then
  reason=$(curl -sS --max-time 15 "$API?symbol=BTCUSDT" 2>&1 >/dev/null | head -1)
  miss "Binance доступен" "${reason:-нет ответа}"
  miss "документированная команда" "сеть недоступна"
  miss "неверный символ через API" "сеть недоступна"
else
  ok "Binance доступен"

  out=$(curl -sS -g --max-time 20 "$API?symbols=[\"BTCUSDT\",\"ETHUSDT\"]" | python3 "$FMT" 2>&1); code=$?
  if [ "$code" -eq 0 ] && printf '%s' "$out" | grep -q BTCUSDT && printf '%s' "$out" | grep -q ETHUSDT; then
    ok "документированная команда (-sS -g, два символа)"
    printf '%s\n' "$out" | sed 's/^/        /'
  else
    bad "документированная команда (-sS -g, два символа)" "код $code: $(printf '%s' "$out" | head -2 | tr '\n' ' ')"
  fi

  out=$(curl -sS --max-time 20 "$API?symbol=NOSUCHPAIR" | python3 "$FMT" 2>&1); code=$?
  if [ "$code" -eq 1 ]; then ok "неверный символ → код 1, сообщение биржи: $(printf '%s' "$out" | head -1)"
  else bad "неверный символ → код 1" "код $code: $(printf '%s' "$out" | head -1)"; fi
fi

echo
printf 'Итог: %d пройдено, %d провалено, %d пропущено\n' "$pass" "$fail" "$skip"
[ "$skip" -gt 0 ] && echo "Сетевые проверки пропущены — цепочка целиком НЕ подтверждена."
[ "$fail" -eq 0 ] || exit 1
