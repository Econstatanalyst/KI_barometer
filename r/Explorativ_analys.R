

# -------------------------------------------------------------
# Installera paket om de saknas
# -------------------------------------------------------------

if (!require("duckdb"))  install.packages("duckdb")
if (!require("dplyr"))   install.packages("dplyr")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("tidyr"))   install.packages("tidyr")

library(duckdb)
library(dplyr)
library(ggplot2)
library(tidyr)


# -------------------------------------------------------------
# Ladda in data från DuckDB
# -------------------------------------------------------------

con <- dbConnect(duckdb(), dbdir = "ki_barometer.duckdb", read_only = TRUE)

df <- dbGetQuery(con, "SELECT * FROM analystabell ORDER BY datum")

dbDisconnect(con)

# Konvertera datum-kolumnen till Date-format
df$datum <- as.Date(df$datum)

cat("Antal rader:", nrow(df), "\n")
cat("Kolumner:", paste(names(df), collapse = ", "), "\n\n")


# -------------------------------------------------------------
# Snabbkontroll av datan
# -------------------------------------------------------------

summary(df[, c("barometerindikator", "kpi_arsforandring_pct", "styranta_pct")])


# -------------------------------------------------------------
# Graf 1: De tre tidsserierna
# -------------------------------------------------------------

# Forma om datan till långt format för ggplot
df_long <- df %>%
  select(datum, barometerindikator, kpi_arsforandring_pct, styranta_pct) %>%
  pivot_longer(
    cols      = -datum,
    names_to  = "variabel",
    values_to = "varde"
  ) %>%
  mutate(variabel = recode(variabel,
                           "barometerindikator"    = "KI barometer (index)",
                           "kpi_arsforandring_pct" = "KPI årsförändring (%)",
                           "styranta_pct"          = "Styrränta (%)"
  ))

p1 <- ggplot(df_long, aes(x = datum, y = varde, color = variabel)) +
  geom_line(linewidth = 0.8) +
  facet_wrap(~ variabel, ncol = 1, scales = "free_y") +
  labs(
    title    = "KI barometer, KPI och styrränta 1996–2024",
    subtitle = "Rådata från KI, SCB och Riksbanken",
    x        = NULL,
    y        = NULL,
    caption  = "Källor: Konjunkturinstitutet, SCB, Riksbanken"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

print(p1)
ggsave("r/graf_01_tidsserier.png", p1, width = 12, height = 8, dpi = 150, bg = "white")
cat("Graf sparad: r/graf_01_tidsserier.png\n")



# -------------------------------------------------------------
# Enkel korrelationsanalys
# -------------------------------------------------------------

cat("\n--- Korrelation: barometern vs KPI årsförändring ---\n")

# Samtida korrelation (barometern och KPI samma månad)
kor_0  <- cor(df$barometerindikator, df$kpi_arsforandring_pct, use = "complete.obs")

# Korrelation med LAG (barometern X månader före KPI)
kor_3  <- cor(df$barometer_lag3,  df$kpi_arsforandring_pct, use = "complete.obs")
kor_6  <- cor(df$barometer_lag6,  df$kpi_arsforandring_pct, use = "complete.obs")
kor_12 <- cor(df$barometer_lag12, df$kpi_arsforandring_pct, use = "complete.obs")

cat(sprintf("Samtida (lag 0):   r = %.3f\n", kor_0))
cat(sprintf("Barometer lag 3:   r = %.3f\n", kor_3))
cat(sprintf("Barometer lag 6:   r = %.3f\n", kor_6))
cat(sprintf("Barometer lag 12:  r = %.3f\n", kor_12))

# -------------------------------------------------------------
# Graf: Korrelation mellan barometern och KPI per LAG
# -------------------------------------------------------------

korrelationer <- data.frame(
  lag   = c("Samtida\n(lag 0)", "3 månader\n(lag 3)", "6 månader\n(lag 6)", "12 månader\n(lag 12)"),
  r     = c(kor_0, kor_3, kor_6, kor_12)
)

# Behåll ordningen på x-axeln
korrelationer$lag <- factor(korrelationer$lag, levels = korrelationer$lag)

p3 <- ggplot(korrelationer, aes(x = lag, y = r)) +
  geom_col(fill = "#1f77b4", width = 0.5) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.5) +
  geom_text(aes(label = sprintf("r = %.3f", r)),
            vjust = -0.5, size = 4) +
  scale_y_continuous(limits = c(-0.2, 0.5)) +
  labs(
    title    = "Korrelation: KI barometer vs KPI-inflation",
    subtitle = "Hur starkt samband finns beroende på tidsfördröjning?",
    x        = "Barometerns tidsfördröjning",
    y        = "Korrelationskoefficient (r)",
    caption  = "Källor: Konjunkturinstitutet, SCB"
  ) +
  theme_minimal()

print(p3)
ggsave("r/graf_02_korrelation.png", p3, width = 8, height = 6, dpi = 150, bg = "white")
cat("Graf sparad: r/graf_02_korrelation.png\n")


# Korrelation: barometern vs styrräntan
kor_ranta_0  <- cor(df$barometerindikator, df$styranta_pct, use = "complete.obs")
kor_ranta_3  <- cor(df$barometer_lag3,  df$styranta_pct, use = "complete.obs")
kor_ranta_6  <- cor(df$barometer_lag6,  df$styranta_pct, use = "complete.obs")
kor_ranta_12 <- cor(df$barometer_lag12, df$styranta_pct, use = "complete.obs")

cat("--- Korrelation: barometern vs styrräntan ---\n")
cat(sprintf("Samtida (lag 0):   r = %.3f\n", kor_ranta_0))
cat(sprintf("Barometer lag 3:   r = %.3f\n", kor_ranta_3))
cat(sprintf("Barometer lag 6:   r = %.3f\n", kor_ranta_6))
cat(sprintf("Barometer lag 12:  r = %.3f\n", kor_ranta_12))

# -------------------------------------------------------------
# Graf: Korrelation mellan barometern och styrräntan per LAG
# -------------------------------------------------------------

kor_ranta_df <- data.frame(
  lag = c("Samtida\n(lag 0)", "3 månader\n(lag 3)", "6 månader\n(lag 6)", "12 månader\n(lag 12)"),
  r   = c(kor_ranta_0, kor_ranta_3, kor_ranta_6, kor_ranta_12)
)

kor_ranta_df$lag <- factor(kor_ranta_df$lag, levels = kor_ranta_df$lag)

p4 <- ggplot(kor_ranta_df, aes(x = lag, y = r)) +
  geom_col(fill = "#2ca02c", width = 0.5) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.5) +
  geom_text(aes(label = sprintf("r = %.3f", r)),
            vjust = 1.5, size = 4, color = "white") +
  scale_y_continuous(limits = c(-0.4, 0.1)) +
  labs(
    title    = "Korrelation: KI barometer vs styrränta",
    subtitle = "Negativt samband – hög ränta, lägre stämningsläge",
    x        = "Barometerns tidsfördröjning",
    y        = "Korrelationskoefficient (r)",
    caption  = "Källor: Konjunkturinstitutet, Riksbanken"
  ) +
  theme_minimal()

print(p4)
ggsave("r/graf_03_korrelation_ranta.png", p4, width = 8, height = 6, dpi = 150, bg = "white")
cat("Graf sparad: r/graf_03_korrelation_ranta.png\n")

# -------------------------------------------------------------
# Korrelation: KPI inflation vs styrräntan
# -------------------------------------------------------------

kor_kpi_ranta_0  <- cor(df$kpi_arsforandring_pct, df$styranta_pct, use = "complete.obs")
kor_kpi_ranta_3  <- cor(df$kpi_arsforandring_pct[4:nrow(df)], df$styranta_pct[1:(nrow(df)-3)], use = "complete.obs")
kor_kpi_ranta_6  <- cor(df$kpi_arsforandring_pct[7:nrow(df)], df$styranta_pct[1:(nrow(df)-6)], use = "complete.obs")
kor_kpi_ranta_12 <- cor(df$kpi_arsforandring_pct[13:nrow(df)], df$styranta_pct[1:(nrow(df)-12)], use = "complete.obs")

cat("--- Korrelation: KPI inflation vs styrräntan ---\n")
cat(sprintf("Samtida (lag 0):   r = %.3f\n", kor_kpi_ranta_0))
cat(sprintf("Styrränta lag 3:   r = %.3f\n", kor_kpi_ranta_3))
cat(sprintf("Styrränta lag 6:   r = %.3f\n", kor_kpi_ranta_6))
cat(sprintf("Styrränta lag 12:  r = %.3f\n", kor_kpi_ranta_12))

# -------------------------------------------------------------
# Graf: Korrelation mellan styrräntan och KPI-inflation per LAG
# -------------------------------------------------------------

kor_kpi_ranta_df <- data.frame(
  lag = c("Samtida\n(lag 0)", "3 månader\n(lag 3)", "6 månader\n(lag 6)", "12 månader\n(lag 12)"),
  r   = c(kor_kpi_ranta_0, kor_kpi_ranta_3, kor_kpi_ranta_6, kor_kpi_ranta_12)
)

kor_kpi_ranta_df$lag <- factor(kor_kpi_ranta_df$lag, levels = kor_kpi_ranta_df$lag)

p5 <- ggplot(kor_kpi_ranta_df, aes(x = lag, y = r)) +
  geom_col(fill = "#d62728", width = 0.5) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.5) +
  geom_text(aes(label = sprintf("r = %.3f", r)),
            vjust = -0.5, size = 4, color = "black") +
  scale_y_continuous(limits = c(-0.5, 0.3)) +
  labs(
    title    = "Korrelation: styrränta vs KPI-inflation",
    subtitle = "Hur väl följer styrräntan inflationen?",
    x        = "Styrräntans tidsfördröjning",
    y        = "Korrelationskoefficient (r)",
    caption  = "Källor: Riksbanken, SCB"
  ) +
  theme_minimal()

print(p5)
ggsave("r/graf_04_korrelation_kpi_ranta.png", p5, width = 8, height = 6, dpi = 150, bg = "white")
cat("Graf sparad: r/graf_04_korrelation_kpi_ranta.png\n")



# -------------------------------------------------------------
#  Graf: Spearmans korrelation per period och tidsfördröjning.
# -------------------------------------------------------------

perioder_alla <- c("1996-2024", "Lugn period", "IT-kris", "Finanskris", "Energikris")

kor_alla <- do.call(rbind, lapply(perioder_alla, function(per) {
  if (per == "1996-2024") {
    df_p <- df
  } else {
    df_p <- df[df$krisperiod == per, ]
  }
  data.frame(
    period = per,
    lag    = c("Lag 3", "Lag 6", "Lag 12"),
    r      = c(
      cor.test(df_p$barometer_lag3,  df_p$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")$estimate,
      cor.test(df_p$barometer_lag6,  df_p$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")$estimate,
      cor.test(df_p$barometer_lag12, df_p$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")$estimate
    )
  )
}))

kor_alla$period <- factor(kor_alla$period, levels = perioder_alla)
kor_alla$lag    <- factor(kor_alla$lag, levels = c("Lag 3", "Lag 6", "Lag 12"))

p6 <- ggplot(kor_alla, aes(x = period, y = r, fill = lag)) +
  geom_col(position = "dodge", width = 0.6) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.5) +
  geom_text(aes(label = sprintf("%.2f", r),
                vjust = ifelse(kor_alla$r >= 0, -0.5, 1.5)),
            position = position_dodge(width = 0.6),
            size = 3, color = "black") +
  scale_fill_manual(values = c(
    "Lag 3"  = "#aec7e8",
    "Lag 6"  = "#1f77b4",
    "Lag 12" = "#08306b"
  )) +
  scale_y_continuous(limits = c(-0.6, 1.1)) +
  labs(
    title    = "Barometerns förutsägande förmåga per period och tidsfördröjning",
    subtitle = "Spearmans rangkorrelation mellan barometern och KPI-inflation",
    x        = NULL,
    y        = "Korrelationskoefficient (rho)",
    fill     = "Tidsfördröjning",
    caption  = "Källor: Konjunkturinstitutet, SCB"
  ) +
  theme_minimal()

print(p6)
ggsave("r/graf_05_korrelation_per_period.png", p6, width = 11, height = 6, dpi = 150, bg = "white")
cat("Graf sparad: r/graf_05_korrelation_per_period.png\n")

# -------------------------------------------------------------
# Undersök fördelningen av barometern och KPI-inflation
# -------------------------------------------------------------
png("r/graf_06_fordelning.png", width = 1400, height = 1000, res = 150)
par(mfrow = c(2, 2))

# Histogram för barometern
hist(df$barometerindikator, 
     main = "KI barometer", 
     xlab = "Index", 
     col = "#1f77b4",
     breaks = 20)

# Histogram för KPI-inflation
hist(df$kpi_arsforandring_pct, 
     main = "KPI årsförändring", 
     xlab = "Procent", 
     col = "#d62728",
     breaks = 20)

# QQ-plot för barometern
qqnorm(df$barometerindikator, main = "QQ-plot: KI barometer")
qqline(df$barometerindikator, col = "red")

# QQ-plot för KPI-inflation
qqnorm(df$kpi_arsforandring_pct, main = "QQ-plot: KPI årsförändring")
qqline(df$kpi_arsforandring_pct, col = "red")

dev.off()
par(mfrow = c(1, 1))
cat("Graf sparad: r/graf_06_fordelning.png\n")

# -------------------------------------------------------------
# Scatterplot: barometer lag 12 vs KPI per krisperiod och icke uppdelad period
# -------------------------------------------------------------

# Skapa dataset där varje rad finns både i sin krisperiod och i "1996-2024"
df_scatter <- bind_rows(
  df %>% filter(!is.na(barometer_lag12)) %>% mutate(panel = "1996-2024"),
  df %>% filter(!is.na(barometer_lag12)) %>% mutate(panel = krisperiod)
)

df_scatter$panel <- factor(df_scatter$panel,
                           levels = c("1996-2024", "Lugn period", "IT-kris", "Finanskris", "Energikris"))

p7 <- ggplot(df_scatter,
             aes(x = barometer_lag12, y = kpi_arsforandring_pct, color = panel)) +
  geom_point(alpha = 0.6, size = 2) +
  geom_smooth(method = "loess", se = FALSE, linewidth = 0.8) +
  facet_wrap(~ panel, scales = "free") +
  scale_color_manual(values = c(
    "1996-2024"   = "#2ca02c",
    "Lugn period" = "#1f77b4",
    "IT-kris"     = "#ff7f0e",
    "Finanskris"  = "#d62728",
    "Energikris"  = "#9467bd"
  )) +
  labs(
    title    = "Barometern (lag 12) vs KPI-inflation per period",
    subtitle = "Varje punkt = en månad",
    x        = "KI barometer 12 månader tidigare",
    y        = "KPI årsförändring (%)",
    caption  = "Källor: Konjunkturinstitutet, SCB"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

print(p7)
ggsave("r/graf_07_scatter_per_period.png", p7, width = 10, height = 8, dpi = 150, bg = "white")
cat("Graf sparad: r/graf_07_scatter_per_period.png\n")

# -------------------------------------------------------------
# Spearmans rangkorrelation: barometer vs KPI per period
# -------------------------------------------------------------

# Hela perioden
sp_3  <- cor.test(df$barometer_lag3,  df$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")
sp_6  <- cor.test(df$barometer_lag6,  df$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")
sp_12 <- cor.test(df$barometer_lag12, df$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")

cat("--- Spearmans rangkorrelation: barometer vs KPI ---\n")
cat(sprintf("Barometer lag 3:   rho = %.3f, p = %.4f\n", sp_3$estimate,  sp_3$p.value))
cat(sprintf("Barometer lag 6:   rho = %.3f, p = %.4f\n", sp_6$estimate,  sp_6$p.value))
cat(sprintf("Barometer lag 12:  rho = %.3f, p = %.4f\n", sp_12$estimate, sp_12$p.value))

for (period_namn in c("Lugn period", "IT-kris", "Finanskris", "Energikris")) {
  cat(sprintf("\n--- %s ---\n", period_namn))
  df_p <- df[df$krisperiod == period_namn, ]
  t3  <- cor.test(df_p$barometer_lag3,  df_p$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")
  t6  <- cor.test(df_p$barometer_lag6,  df_p$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")
  t12 <- cor.test(df_p$barometer_lag12, df_p$kpi_arsforandring_pct, method = "spearman", use = "complete.obs")
  cat(sprintf("Lag 3:   rho = %.3f, p = %.4f\n", t3$estimate,  t3$p.value))
  cat(sprintf("Lag 6:   rho = %.3f, p = %.4f\n", t6$estimate,  t6$p.value))
  cat(sprintf("Lag 12:  rho = %.3f, p = %.4f\n", t12$estimate, t12$p.value))
}


# -------------------------------------------------------------
# Tabell: Spearmans rangkorrelation med signifikansstjärnor
# -------------------------------------------------------------

if (!require("gt"))       install.packages("gt")
if (!require("webshot2")) install.packages("webshot2")
library(gt)
library(webshot2)

# Funktion för signifikansstjärnor
stjarnor <- function(p) {
  ifelse(p < 0.001, "***",
         ifelse(p < 0.01,  "**",
                ifelse(p < 0.05,  "*", "")))
}

sp_tabell <- data.frame(
  Period = rep(c("1996-2024", "Lugn period", "IT-kris", "Finanskris", "Energikris"), each = 3),
  Tidsfördröjning = rep(c("3 månader", "6 månader", "12 månader"), 5),
  rho = c(round(sp_3$estimate, 3), round(sp_6$estimate, 3), round(sp_12$estimate, 3),
          0.382, 0.436, 0.418,
          -0.352, 0.101, 0.564,
          0.912, 0.960, 0.823,
          -0.377, 0.101, 0.815),
  p = c(round(sp_3$p.value, 4), round(sp_6$p.value, 4), round(sp_12$p.value, 4),
        0.0000, 0.0000, 0.0000,
        0.1082, 0.6562, 0.0062,
        0.0002, 0.0000, 0.0034,
        0.0233, 0.5566, 0.0000)
)

# Lägg till stjärnor på p-värdet
sp_tabell$p_stjarna <- paste0(format(sp_tabell$p, nsmall = 4), stjarnor(sp_tabell$p))

tabell <- sp_tabell %>%
  select(Period, Tidsfördröjning, rho, p_stjarna) %>%
  gt(groupname_col = "Period") %>%
  tab_header(
    title    = "Spearmans rangkorrelation: barometern vs KPI-inflation",
    subtitle = "Uppdelat på tidsperiod och tidsfördröjning"
  ) %>%
  cols_label(
    Tidsfördröjning = "Tidsfördröjning",
    rho = "rho",
    p_stjarna = "p-värde"
  ) %>%
  tab_style(
    style     = cell_fill(color = "#e8f4e8"),
    locations = cells_row_groups()
  ) %>%
  tab_source_note("* p < 0.05, ** p < 0.01, *** p < 0.001.")

print(tabell)

gtsave(tabell, "r/tabell_01_spearman.png")
cat("Tabell sparad: r/tabell_01_spearman.png\n")