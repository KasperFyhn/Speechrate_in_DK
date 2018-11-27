all.data <- read.csv(choose.files())

## STOP - a possibility to run through with data trimmed for short turns as
## these more often give very high numbers and a more spread distribution
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

data$popdensity = as.numeric(ordered(data$popdensity))
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

full.model <- glmer(speechrate ~ log10(popdensity) + gender + turn.id
                    + (1 + turn.id|speaker/dyad),
                    family=gaussian(link=log), data = data,
                    control = glmerControl(optimizer = "nloptwrap",
                                           calc.derivs = FALSE)
                    )
summary(full.model)
anova(null.model, full.model)
