# souza_et_al_2021.tsv -> Cytoscape bipartite network (sample x phorid parasitoid)
# Sources: sampling events (Date|Site|Colony|Local|Caste). Targets: parasitoid species.

library(tidyverse)

raw <- read_tsv("souza_et_al_2021.tsv", show_col_types = FALSE) %>%
  rename_with(str_trim)          # the header " N_erthali" has a leading space

parasite_cols <- c("A_attophilus", "A_vicosae", "N_erthali", "M_grandicornis")
key_cols      <- c("date_iso", "Site", "Colony", "Local", "Caste")

# Brazilian abbreviated months ("27-fev.-18"). A lookup avoids depending on a
# pt_BR locale being installed, which it often isn't under WSL2.
meses <- c(jan = 1, fev = 2, mar = 3, abr = 4, mai = 5, jun = 6,
           jul = 7, ago = 8, set = 9, out = 10, nov = 11, dez = 12)

parse_data_br <- function(x) {
  p <- str_split_fixed(x, "-", 3)
  m <- meses[str_remove(p[, 2], fixed("."))]
  as.Date(sprintf("20%s-%02d-%02d", p[, 3], m, as.integer(p[, 1])))
}

clean <- raw %>%
  mutate(
    Local    = if_else(Local == "trial", "trail", Local),   # typo, 1 row
    date_iso = parse_data_br(Date)
  ) %>%
  # (Date, Site, Colony, Local, Caste) is NOT unique: four sampling events are
  # repeated within a date. A replicate index keeps them as distinct nodes.
  group_by(across(all_of(key_cols))) %>%
  mutate(rep = row_number()) %>%
  ungroup() %>%
  mutate(sample_id = paste(date_iso, Site, Colony, Local, Caste,
                           paste0("r", rep), sep = "|"))

stopifnot(!any(duplicated(clean$sample_id)))

# ---- edges -----------------------------------------------------------------
edges <- clean %>%
  select(sample_id, No_ants, all_of(parasite_cols)) %>%
  pivot_longer(all_of(parasite_cols), names_to = "parasite", values_to = "count") %>%
  filter(count > 0) %>%
  mutate(
    interaction = "parasitism",
    per_100_ants = round(100 * count / No_ants, 3)
  ) %>%
  select(sample_id, interaction, parasite, count, per_100_ants)

# ---- nodes -----------------------------------------------------------------
nodes_samples <- clean %>%
  transmute(
    id = sample_id,
    node_type = "sample",
    date = as.character(date_iso),
    site = Site, colony = as.character(Colony), local = Local, caste = Caste,
    n_ants = No_ants,
    n_parasitized = No_parasitized_ants,
    prevalence = round(100 * No_parasitized_ants / No_ants, 3)
  )

nodes_parasites <- tibble(id = parasite_cols, node_type = "parasite")

nodes <- bind_rows(nodes_samples, nodes_parasites)

write_tsv(edges, "edges.tsv")
write_tsv(nodes, "nodes.tsv")

# ---- push straight into a running Cytoscape session ------------------------
# Keeps the 175 parasite-free samples as isolated nodes, which a file import
# would silently drop.
#
# library(RCy3)
# cytoscapePing()
# createNetworkFromDataFrames(
#   nodes = nodes %>% rename(group = node_type),
#   edges = edges %>% rename(source = sample_id, target = parasite),
#   title = "Souza et al. 2021", collection = "Atta parasitoids"
# )