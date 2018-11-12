data <- read.csv('/Volumes/dfs/ARTS_Project-Linguistics/Kasper - The Puzzle of Danish/report.csv')
long.turns <- subset(data, dur..s. > 0.5)

# boxplots for all data
boxplot(speechrate ~ city, data, main='Speech rate between cities')
boxplot(speechrate ~ gender*city, data, main='Speech rate between cities and genders')
boxplot(speechrate ~ pop.density, data, xlab='Population density (citizens/square meter)',
        main='Speech rate according to population density')

# boxplots for long turns
boxplot(speechrate ~ city, long.turns, main='Speech rate between cities')
boxplot(speechrate ~ gender*city, long.turns, main='Speech rate between cities and genders')
boxplot(speechrate ~ pop.density, long.turns, xlab='Population density (citizens/square meter)',
        main='Speech rate according to population density')

# fitted histogram for all data
hist(data$speechrate, breaks = 40, prob = TRUE, main='Speech rates - all data (n=61977)',
     xlab='Speech rate', ylab='Proportional frequency')
lines(density(data$speechrate), lty='dotted', lwd=1.5)
lines(density(data$speechrate, adjust=2.5), lwd=2)

# fitted histogram for long turns
hist(long.turns$speechrate, breaks = 30, prob = TRUE, main='Speech rates - turns > 0.5s (n=39479)',
     xlab='Speech rate', ylab='Proportional frequency')
lines(density(long.turns$speechrate), lty='dotted', lwd=1.5)
lines(density(long.turns$speechrate, adjust=2.5), lwd=2)
