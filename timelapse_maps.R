library(dplyr)
library(ggplot2)
library(ggmap)

# This script allows you to create timelapse images of the spread of StemRust in Ethiopia

df <- read.csv('../RustSurvey.csv')
df_months <- read.csv('../RustSurvey_v2.csv')
map <- get_map(location = 'Ethiopia', zoom = 6, maptype = 'terrain')

stem_yes <- df %>% filter(StemRust.Binary == TRUE)

# Heat map of locations that are positive for stem rust
for(year in unique(stem_yes$ObsYear)) {
  year_df <- stem_yes %>% filter(ObsYear == year)
  ggmap(map, extent = "device") + 
    geom_density2d(data = year_df, aes(x = Longitude, y = Latitude), size = 0.5) + 
    stat_density2d(data = year_df, 
                   aes(x = Longitude, y = Latitude, fill = ..level.., alpha = ..level..), size = 0.01, 
                   bins = 16, geom = "polygon") + 
                   scale_fill_gradient(low = "green", high = "red") + 
    scale_alpha(range = c(0, 0.5), guide = FALSE) + 
    ggtitle(paste('Positive Stem rust Cases:', year)) + 
    theme(legend.position = "none")
  ggsave(paste(year, '.png'))
}

# Map the survey locations
for(year in unique(df$ObsYear)) {
  year_df <- df %>% filter(ObsYear == year)
    ggmap(map, extent = "device") + 
      geom_point(data = year_df, aes(x = Longitude, y = Latitude)) + 
      ggtitle(paste('Survey Locations:', year)) + 
      theme(legend.position = "none")
  ggsave(paste(year, 'survey_locations.png'))
}

# Map the survey locations and postive or negative

for(year in unique(df$ObsYear)) {
  year_df <- df %>% filter(ObsYear == year) %>% mutate(StemRust.Binary = ifelse(is.na(StemRust.Binary), FALSE, StemRust.Binary))
  ggmap(map, darken = c(0.4, "white"), extent = "device") + 
    geom_point(data = year_df, aes(x = Longitude, y = Latitude, color = StemRust.Binary), alpha = .3) + 
    scale_color_manual(values=c("black", "red")) + 
    ggtitle(paste('StemRust_Location:', year)) 
  ggsave(paste('stem_rust_binary_location', year, '.png'))
}

year_df <- df %>% filter(ObsYear == 2009) %>% mutate(StemRust.Binary = ifelse(is.na(StemRust.Binary), FALSE, StemRust.Binary))
