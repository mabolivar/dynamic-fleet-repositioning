#' ***********************************
#' Value function explroation
#' ***********************************

### Packages -----------------

library("tidyverse")
library("jsonlite")
library(gganimate)
library(gifski)

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
         lng_p = lng + lng_p) %>% 
  mutate_at(vars(lat_p, lng_p), as.character)
  
# Get best neighbor per location

df_best_move <- df %>%
  filter(scenario %in% c(0:5)) %>% 
  split(paste(.$instance, .$scenario, .$epoch)) %>% 
  map_df(.f=~df_neighbours %>% 
        inner_join(.x %>% mutate_at(vars(lat, lng), as.character),
                   by=c('lat_p'='lat', 'lng_p'='lng')) %>%
        group_by(instance, scenario, epoch, lat, lng) %>% 
        filter(value == min(value)) %>% 
        ungroup %>% 
        mutate_at(vars(lat_p, lng_p), as.numeric)
      )

### Visualization -----------------
# Vector plot
to_plot <- df_best_move %>% 
  mutate(epoch = as.integer(epoch)) %>% 
  filter(epoch == 21 * 60 / 10, 
         instance == 'test',
         scenario == 2) %>% 
  semi_join(df_cords)

p <- ggplot(data = to_plot) +
  geom_point(aes(x=lng, y = lat), size = 0.5) +
  geom_segment(
    aes(x=lng, y = lat, xend=lng_p, yend=lat_p, color=value), 
    alpha = 0.5,
    arrow = arrow(length=unit(0.05,"cm"), ends="last", type = "closed")
    ) +
  scale_color_viridis_c(option = "B", direction = -1) +
  theme_minimal()

p

# Vector plot evolution
to_plot <- df_best_move %>% 
  mutate(epoch = as.integer(epoch)) %>% 
  filter(epoch == 21 * 60 / 10)

p <- ggplot(data = to_plot) +
  geom_point(aes(x=lng, y = lat), size = 0.5) +
  geom_segment(
    aes(x=lng, y = lat, xend=lng_p, yend=lat_p, color=value), 
    alpha = 0.5,
    arrow = arrow(length=unit(0.05,"cm"), ends="last", type = "closed")
  ) +
  scale_color_viridis_c(option = "B", direction = -1) +
  facet_grid(instance ~ scenario) + 
  theme_minimal()

p


# Heatmap plot
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


an <- animate(p.animation, height = 500, width = 800, fps = 30, duration = 30,
              end_pause = 3, res = 100, renderer = gifski_renderer())
anim_save("module1_hex30secs30fps.gif", animation= an, path = 'animations')



# Contour plot
to_plot <- df %>% 
  filter(as.integer(epoch) %% 1 == 0) %>% 
  mutate(epoch = as.integer(epoch) * 10 / 60) %>% 
  filter(scenario == 2)


p <- ggplot(data = to_plot) +
  geom_tile(aes(x=lng, y = lat, fill = value)) +
  scale_fill_viridis_c(option = "B", direction = -1) +
  facet_wrap(instance + scenario ~ .) +
  theme_minimal()

p.animation = p +
  transition_manual(epoch) +
  labs(subtitle = "Epoch: {current_frame}")


an <- animate(p.animation, height = 600, width = 1600, fps = 20, duration = 20,
              end_pause = 3, res = 100, renderer = gifski_renderer())
anim_save("start_end_hex20secs.gif", animation= an, path = 'animations')

# Scenario evolution - Value function
max_train_scenario = df %>% 
  filter(instance == 'train') %>% 
  pull(scenario) %>%
  as.integer() %>% 
  max
to_plot <- df %>% 
  filter(as.integer(epoch) == 21 * 60 / 10) %>% 
  mutate(epoch = as.integer(epoch) * 10 / 60,
         scenario = as.integer(scenario),
         scenario = if_else(
           instance == 'test', 
           scenario + 1L + max_train_scenario, 
           scenario
           )
         )

p <- ggplot(data = to_plot) +
  geom_tile(aes(x=lng, y = lat, fill = value)) +
  scale_fill_viridis_c(option = "B", direction = -1) +
  theme_minimal()

p.animation = p +
  transition_manual(scenario) +
  labs(subtitle = "Scenario: {current_frame}")


an <- animate(p.animation, height = 500, width = 800, fps = 20, duration = 20,
              end_pause = 3, res = 100, renderer = gifski_renderer())
anim_save("scenario_evolution_hex20secs.gif", animation= an, path = 'animations')

