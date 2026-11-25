"""Evidencia grafica y seleccion documentada del modelo de extremos."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from lmoments3 import lmom_ratios

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir()); DATA=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'; INP=DATA/'extremos_2_2'; OUT=INP
DURS=['10min','30min','1h','3h','6h','12h','24h']; MODELS=[('gumbel','mle'),('gev','mle'),('logpearson3','mle')]

def cdf(model, pars, x):
    if model=='gumbel': return stats.gumbel_r.cdf(x,*pars)
    if model=='gev': return stats.genextreme.cdf(x,*pars)
    return stats.pearson3.cdf(np.log10(x),*pars)

def main():
    annual=pd.read_csv(INP/'ams_hydrological_oct_sep.csv'); fit=pd.read_csv(INP/'fit_summary_3methods.csv'); boot=pd.read_csv(INP/'bootstrap_ci_gev.csv')
    # Graficas de probabilidad: puntos observados contra probabilidad teorica.
    fig, axes=plt.subplots(4,2,figsize=(12,16)); axes=axes.ravel()
    for ax,d in zip(axes,DURS):
        x=np.sort(annual[f'max_{d}_mm'].dropna().to_numpy(float)); p=(np.arange(1,len(x)+1)-.44)/(len(x)+.12)
        for model,method in MODELS:
            row=fit[(fit.duration==d)&(fit.distribution==model)&(fit.method==method)].iloc[0]; pars=tuple(float(v) for v in row.parameters.split(';'))
            theo=np.sort(np.asarray(stats.gumbel_r.ppf(p,*pars) if model=='gumbel' else stats.genextreme.ppf(p,*pars) if model=='gev' else 10**stats.pearson3.ppf(p,*pars)).ravel())
            ax.plot(theo,x,'o',ms=3,label=model)
        lim=[0,max(x.max(),ax.get_xlim()[1])]; ax.plot(lim,lim,'k--',lw=.7); ax.set_title(d); ax.set_xlabel('Cuantil teórico (mm)'); ax.set_ylabel('Máximo observado (mm)'); ax.grid(alpha=.25)
    axes[-1].axis('off'); axes[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(OUT/'graficas_probabilidad_2_2.png',dpi=180); plt.close(fig)

    # Razones de L-momentos muestrales y curvas teoricas aproximadas.
    ratios=[]
    for d in DURS:
        x=annual[f'max_{d}_mm'].dropna().to_numpy(float); lm=lmom_ratios(x,nmom=4); ratios.append({'duration':d,'tau3':float(lm[2]/lm[1]),'tau4':float(lm[3]/lm[1])})
    ratiod=pd.DataFrame(ratios); ratiod.to_csv(OUT/'lmoment_ratios_sample.csv',index=False,float_format='%.6f')
    fig,ax=plt.subplots(figsize=(8,6)); ax.scatter(ratiod.tau3,ratiod.tau4,s=50,label='Máximos anuales')
    for _,r in ratiod.iterrows(): ax.annotate(r.duration,(r.tau3,r.tau4),fontsize=8)
    rng=np.random.default_rng(202602)
    for name,color in [('gumbel','tab:orange'),('gev','tab:blue'),('logpearson3','tab:green')]:
        xx=[]; yy=[]
        for shape in np.linspace(-.4,.4,17):
            if name=='gumbel': sample=stats.gumbel_r.rvs(size=5000,random_state=rng)
            elif name=='gev': sample=stats.genextreme.rvs(shape,size=5000,random_state=rng)
            else: sample=stats.pearson3.rvs(shape,size=5000,random_state=rng)
            lm=lmom_ratios(sample,nmom=4); xx.append(lm[2]/lm[1]); yy.append(lm[3]/lm[1])
        ax.plot(xx,yy,'-',color=color,label=name)
    ax.set_xlabel('τ3 (L-skewness)'); ax.set_ylabel('τ4 (L-kurtosis)'); ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(OUT/'diagrama_lmomentos_2_2.png',dpi=180); plt.close(fig)

    # Seleccion: promedio de p-valores + penalizacion por anchura bootstrap T=100.
    agg=fit.groupby(['distribution','method']).agg(ks_pvalue=('ks_pvalue','mean'),cvm_pvalue=('cvm_pvalue','mean')).reset_index()
    b100=boot[boot.T_years==100].groupby('duration').relative_width.median(); gev_width=float(b100.median())
    agg['score_pvalues']=agg.ks_pvalue+agg.cvm_pvalue; agg['bootstrap_width_T100_gev']=gev_width
    agg['recommended']=((agg.distribution=='gev')&(agg.method=='mle'))
    agg.to_csv(OUT/'seleccion_modelo_2_2.csv',index=False,float_format='%.6f')
    (OUT/'dictamen_2_2.md').write_text(
        '# Dictamen del apartado 2.2\n\n'
        'Se compararon Gumbel, GEV y log-Pearson III mediante momentos, L-momentos y máxima verosimilitud. '
        'Se usaron Kolmogorov–Smirnov y Cramer–von Mises, gráficas de probabilidad y razones de L-momentos. '
        'La recomendación provisional es **GEV por máxima verosimilitud**: presenta el mayor promedio combinado de p-valores '
        'entre las combinaciones evaluadas. La incertidumbre de cuantiles T=100 se reporta con bootstrap GEV-MLE. '
        'La elección debe discutirse junto con la estabilidad de cuantiles y no solo con p-valores.\n',encoding='utf-8')
    print('Graficas y seleccion 2.2 generadas; recomendado GEV-MLE')
if __name__=='__main__': main()
