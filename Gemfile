# frozen_string_literal: true

source "https://rubygems.org"

# Tema Chirpy consumido como gem (forma recomendada pelo projeto).
# Manter a versão fixada facilita auditar atualizações do tema.
gem "jekyll-theme-chirpy", "~> 7.2"

# Necessário no Ruby 3.4+, onde estas saíram da biblioteca padrão.
gem "csv"
gem "base64"
gem "bigdecimal"

group :test do
  gem "html-proofer", "~> 5.0"
end

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end
