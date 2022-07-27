#' ***********************************
#' Value function explroation
#' ***********************************

### Packages -----------------

library("tidyverse")
library("jsonlite")

### Function -----------------
load_and_parse_json <- function(file_path, file_name){
  parsed_named = str_split(file_name, pattern = "_", simplify = T)
  instance_label = parsed_named[1]
  scenario_id = parsed_named[2]
  
  df_V = read_json(file_path)[["V"]] %>% 
    map2_df(., names(.), 
            .f= ~.x %>% 
              unlist(recursive = FALSE) %>% 
              enframe()  %>% 
              mutate(
                instance = instance_label,
                scenario = scenario_id, 
                epoch=.y,
                name = str_remove_all(name, "\\(|\\)|[:blank:]")
                ) %>%  
              separate(name, into=c('lat', 'lng'), sep = ",") %>% 
              mutate_at(.vars = vars(lat,lng), .funs = as.numeric)
    )
  
  return(df_V)
}

### Load data ----------------
data_path = './logs/robotex5/VFA/'
files = dir(data_path, full.names = T)

file_names = map_chr(files, 
                     .f=~str_split(.x, "/", simplify = T) %>% 
                       .[length(.)] %>% 
                       str_remove("\\..+")
                     )

df <- map2_df(.x=files, .y=file_names, .f=~load_and_parse_json(.x, .y))


### Tidy data  ----------------

# Filter coordinates
df_cords = df %>% 
  select(lat, lng) %>% 
  distinct() %>% 
  filter(between(lat, 59.1,60), between(lng, 23,25.5))

# Build neigbours
precision <- 2
scale = 10 ** precision
df_perturbation <- merge(
  tibble(lat_p = c(0, 1, -1) / scale), 
  tibble(lng_p = c(0, 1, -1) / scale)
  )

df_neighbours <- merge(df_cords, df_perturbation) %>% 
  as_tibble() %>% 
  mutate(lat_p = lat + lat_p,
         lng_p = lng + lng_p)
  
# Get best neighbor per location

df_best_move <- df %>%
  filter(scenario %in% c(0:5)) %>% 
  split(paste(.$instance, .$scenario, .$epoch)) %>% 
  map_df(.f=~df_neighbours %>% 
        inner_join(.x, by=c('lat_p'='lat', 'lng_p'='lng')) %>%
        group_by(instance, scenario, epoch, lat, lng) %>% 
        filter(value == min(value)) %>% 
        ungroup
      )

### Visualization -----------------
# Vector plot
to_plot <- df_best_move %>% 
  mutate(epoch = as.integer(epoch) * 10 / 60) %>% 
  filter(epoch %in% c(0, 13 * 6, 21 * 6), 
         instance == 'test',
         scenario == 2) %>% 
  semi_join(df_cords)

p <- ggplot(data = to_plot) +
  geom_point(aes(x=lng, y = lat), size = 0.5) +
  geom_segment(
    aes(x=lng, y = lat, xend=lng_p, yend=lat_p), 
    alpha = 0.5,
    arrow = arrow(length=unit(0.05,"cm"), ends="last", type = "closed")
    ) +
  theme_minimal()

p

# tile plot

# Contour plot
to_plot <- df %>% 
  filter(as.integer(epoch) %% 100 == 0) %>% 
  mutate(epoch = as.integer(epoch) * 10 / 60) %>% 
  filter(instance == 'test',
         scenario == 2) %>% 
  semi_join(df_cords)

ggplot(data = to_plot) +
  geom_tile(aes(x=lng, y = lat, fill = value)) +
  scale_fill_viridis_c(option = "B", direction = -1) +
  facet_grid(epoch ~ .) +
  theme_minimal()

#### Animation ----------------------------
library(gganimate)
library(gifski)

# Arrows
to_plot <- df_best_move %>% 
  filter(as.integer(epoch) %% 1 == 0) %>% 
  mutate(epoch = as.integer(epoch) * 10 / 60) %>% 
  filter(instance == 'test',
         scenario == 2) %>% 
  semi_join(df_cords)

p <- ggplot(data = to_plot) +
  geom_point(aes(x=lng, y = lat), size = 0.5) +
  geom_segment(
    aes(x=lng, y = lat, xend=lng_p, yend=lat_p), 
    alpha = 0.5,
    arrow = arrow(length=unit(0.05,"cm"), ends="last", type = "closed")
  ) +
  theme_minimal()

p.animation = p +
  transition_manual(epoch) +
  labs(subtitle = "Epoch: {current_frame}")


an <- animate(p.animation, height = 500, width = 800, fps = 20, duration = 30,
              end_pause = 3, res = 100, renderer = gifski_renderer())
anim_save("module1_30secs.gif", animation= an, path = 'animations')

# Contour plot
to_plot <- df %>% 
  filter(as.integer(epoch) %% 1 == 0) %>% 
  mutate(epoch = as.integer(epoch) * 10 / 60) %>% 
  filter(instance == 'test',
         scenario == 2) %>% 
  semi_join(df_cords)


p <- ggplot(data = to_plot) +
  geom_tile(aes(x=lng, y = lat, fill = value)) +
  scale_fill_viridis_c(option = "B", direction = -1) +
  theme_minimal()

p.animation = p +
  transition_manual(epoch) +
  labs(subtitle = "Epoch: {current_frame}")


an <- animate(p.animation, height = 500, width = 800, fps = 20, duration = 10,
              end_pause = 3, res = 100, renderer = gifski_renderer())
anim_save("module1_hex10secs.gif", animation= an, path = 'animations')
