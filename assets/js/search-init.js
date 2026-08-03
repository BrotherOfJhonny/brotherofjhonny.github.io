---
layout: compress
permalink: /assets/js/search-init.js
---

/*
 * Inicialização da busca.
 *
 * O tema Chirpy emite este código como <script> inline. Aqui ele virou
 * arquivo externo para que a CSP possa usar `script-src 'self'` sem
 * precisar de 'unsafe-inline', que enfraqueceria a proteção contra XSS
 * no site inteiro.
 *
 * Depende da biblioteca Simple-Jekyll-Search (MIT), carregada localmente
 * a partir de /assets/lib/ pelo modo auto-hospedado do tema.
 */

{% capture resultado %}
<article class="px-1 px-sm-2 px-lg-4 px-xl-0">
  <header>
    <h2><a href="{url}">{title}</a></h2>
    <div class="post-meta d-flex flex-column flex-sm-row text-muted mt-1 mb-1">
      {categories}
      {tags}
    </div>
  </header>
  <p>{content}</p>
</article>
{% endcapture %}

{% capture sem_resultado %}<p class="mt-5">{{ site.data.locales[site.lang].search.no_results }}</p>{% endcapture %}

document.addEventListener('DOMContentLoaded', function () {
  var entrada = document.getElementById('search-input');
  var saida = document.getElementById('search-results');

  if (!entrada || !saida || typeof SimpleJekyllSearch !== 'function') {
    return;
  }

  function envolver(icone, valor) {
    if (valor === '') {
      return valor;
    }
    return '<div class="me-sm-4"><i class="' + icone + ' fa-fw"></i>' + valor + '</div>';
  }

  SimpleJekyllSearch({
    searchInput: entrada,
    resultsContainer: saida,
    json: '{{ "/assets/js/data/search.json" | relative_url }}',
    searchResultTemplate: '{{ resultado | strip_newlines }}',
    noResultsText: '{{ sem_resultado }}',
    templateMiddleware: function (propriedade, valor) {
      if (propriedade === 'categories') {
        return envolver('far fa-folder', valor);
      }
      if (propriedade === 'tags') {
        return envolver('fa fa-tag', valor);
      }
      return valor;
    }
  });
});
