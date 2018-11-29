all.data <- read.csv(file.choose())
levels(all.data$city) <- list(Skjern='SKERN', Bornholm='BORNHOLM', Nyborg='NYB',
                              Sønderborg='SOEN', Næstved='NAESTV', København='KBH')
levels(all.data$gender) <- list(Female='F', Male='M')
all.data$speechtime = all.data$phon.time / all.data$dur

data <- subset(all.data, nsyll > 1 & dur > 2)


## means (trimmed) and standard deviations
aggregate(data[, 'speechrate'], list(data$city),
          function(x) c(mean = mean(x, trim = 0.05), sd = sd(x),
                        median = median(x), IQR = IQR(x)
                        )
          )

boxplot(speechrate ~ city, data, main='Speech rate between cities',
        ylab='Speech rate (syllables/sec)')
boxplot(speechrate ~ gender*city, data,
        xlab='City and gender',
        ylab='Speech rate (syllables/sec)',
        main='Speech rate between cities and genders')

hist(data$speechrate, breaks = 60, prob = TRUE, main='Speech rates - all data',
     xlab='Speech rate', ylab='Proportional frequency')
lines(density(data$speechrate), lty='dotted', lwd=1.5)
lines(density(data$speechrate, adjust=2.5), lwd=2)

## measures of shape
library(e1071)
skewness(data$speechrate)
2 * sqrt( 6 / nrow(data) ) # too skewed? somewhat, yes
kurtosis(data$speechrate)
4 * sqrt( 6 / nrow(data) ) # kurtosis substantially different from zero? yes

## modeling the data - SPEECH RATE
library(lme4)
null.model <- glmer(speechrate ~ 1 + (1|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
                    )
summary(null.model)

data$popdensity = as.integer(ordered(data$popdensity))
popd.model <- glmer(speechrate ~  popdensity + (1|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
                    )
summary(popd.model)
anova(null.model, popd.model)

gender.model <- glmer(speechrate ~ gender + (1|speaker/dyad),
                      family=gaussian(link=log), data=data,
                      control = glmerControl(optimizer = "nloptwrap",
                                             calc.derivs = FALSE)
                      )
summary(gender.model)
anova(null.model, gender.model)

data$turn.id = scale(data$turn.id)
turn.model <- glmer(speechrate ~ turn.id + (1 + turn.id|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
                    )
summary(turn.model)
anova(null.model, turn.model)

full.model <- glmer(speechrate ~ log10(popdensity) + gender + (1|speaker/dyad),
                    family=gaussian(link=log), data = data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
                    )
summary(full.model)
anova(gender.model, full.model) # test for popd
anova(popd.model, full.model)   # test for gender

## modeling the data - ARTICULATION RATE
library(lme4)
null.model <- glmer(articrate ~ 1 + (1|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
)
summary(null.model)

data$popdensity = as.integer(ordered(data$popdensity))
popd.model <- glmer(articrate ~  popdensity + (1|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
)
summary(popd.model)
anova(null.model, popd.model)

gender.model <- glmer(articrate ~ gender + (1|speaker/dyad),
                      family=gaussian(link=log), data=data,
                      control = glmerControl(optimizer = "nloptwrap",
                                             calc.derivs = FALSE)
)
summary(gender.model)
anova(null.model, gender.model)

full.model <- glmer(articrate ~ log10(popdensity) + gender + (1|speaker/dyad),
                    family=gaussian(link=log), data = data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
)
summary(full.model)
anova(gender.model, full.model) # test for popd
anova(popd.model, full.model)   # test for gender

## modeling the data - SPEECH TIME
null.model <- glmer(speechtime ~ 1 + (1|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
)
summary(null.model)

data$popdensity = as.integer(ordered(data$popdensity))
popd.model <- glmer(speechtime ~  popdensity + (1|speaker/dyad),
                    family=gaussian(link=log), data=data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
)
summary(popd.model)
anova(null.model, popd.model)

gender.model <- glmer(speechtime ~ gender + (1|speaker/dyad),
                      family=gaussian(link=log), data=data,
                      control = glmerControl(optimizer = "nloptwrap",
                                             calc.derivs = FALSE)
)
summary(gender.model)
anova(null.model, gender.model)

full.model <- glmer(speechtime ~ log10(popdensity) + gender + (1|speaker/dyad),
                    family=gaussian(link=log), data = data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
)
summary(full.model)
anova(gender.model, full.model) # test for popd
anova(popd.model, full.model)   # test for gender

# nice plots for the poster
library(ggplot2)
tiff("gender.tiff", units="in", width=5, height=5, res=300)
dev.off()

# popd - SPEECH RATE
ggplot(data, aes(x = reorder(city, popdensity), y = speechrate, fill=city)) +
  geom_violin() +
  geom_boxplot(width = 0.5, outlier.size = 1, fill='white') +
  theme(legend.position = 'none') +
  labs(x = 'Areas ordered by population density',
       y = 'Speech rate (syllables/sec)',
       title = 'Speech rate in different areas')

  
# gender - SPEECH RATE
ggplot(data, aes(x = gender, y = speechrate, fill=gender)) +
  geom_violin() +
  geom_boxplot(width = 0.5, outlier.size = 1, fill='white') +
  theme(legend.position = 'none') +
  labs(x = 'Gender',
       y = 'Speech rate (syllables/sec)',
       title = 'Speech rate between genders')

# popd - ARTIC RATE
ggplot(data, aes(x = reorder(city, popdensity), y = articrate, fill=city)) +
  geom_violin() +
  geom_boxplot(width = 0.5, outlier.size = 1, fill='white') +
  theme(legend.position = 'none') +
  labs(x = 'Areas ordered by population density',
       y = 'Speech rate (syllables/sec)',
       title = 'Speech rate in different areas')


# gender - ARTIC RATE
ggplot(data, aes(x = gender, y = articrate, fill=gender)) +
  geom_violin() +
  geom_boxplot(width = 0.5, outlier.size = 1, fill='white') +
  theme(legend.position = 'none') +
  labs(x = 'Gender',
       y = 'Speech rate (syllables/sec)',
       title = 'Speech rate between genders')

# popd - SPEECH TIME
ggplot(data, aes(x = reorder(city, popdensity), y = speechtime, fill=city)) +
  geom_violin() +
  geom_boxplot(width = 0.5, outlier.size = 1, fill='white') +
  theme(legend.position = 'none') +
  labs(x = 'Areas ordered by population density',
       y = 'Speech rate (syllables/sec)',
       title = 'Speech rate in different areas')


# gender - SPEECH TIME
ggplot(data, aes(x = gender, y = speechtime, fill=gender)) +
  geom_violin() +
  geom_boxplot(width = 0.5, outlier.size = 1, fill='white') +
  theme(legend.position = 'none') +
  labs(x = 'Gender',
       y = 'Speech rate (syllables/sec)',
       title = 'Speech rate between genders')
