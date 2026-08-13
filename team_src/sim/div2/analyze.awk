# sb_quad.dat cols: 1=t 2=I_P 3=t 4=I_N 5=t 6=Q_P 7=t 8=Q_N 9=t 10=INVO3_IP 11=t 12=INVO3_QP
NR>1 {
  t=$1; ip=$2; in_=$4; qp=$6; qn=$8; o3i=$10; o3q=$12;
  T[NR]=t; OI[NR]=o3i; OQ[NR]=o3q; IPv[NR]=ip; N=NR;
  if(t>=16e-9){ n++;
    if(n==1){ipmn=ip;ipmx=ip;inmn=in_;inmx=in_;qpmn=qp;qpmx=qp;qnmn=qn;qnmx=qn;oimn=o3i;oimx=o3i}
    if(ip<ipmn)ipmn=ip; if(ip>ipmx)ipmx=ip;
    if(in_<inmn)inmn=in_; if(in_>inmx)inmx=in_;
    if(qp<qpmn)qpmn=qp; if(qp>qpmx)qpmx=qp;
    if(qn<qnmn)qnmn=qn; if(qn>qnmx)qnmx=qn;
    if(o3i<oimn)oimn=o3i; if(o3i>oimx)oimx=o3i;
  }
}
END{
  midi=(oimx+oimn)/2;
  ei=0; eq=0; fi=0;
  for(k=2;k<=N;k++){ if(T[k]<16e-9)continue;
    if(OI[k-1]<midi&&OI[k]>=midi){EI[++ei]=T[k-1]+(midi-OI[k-1])*(T[k]-T[k-1])/(OI[k]-OI[k-1])}
    if(OI[k-1]>=midi&&OI[k]<midi){FI[++fi]=T[k-1]+(midi-OI[k-1])*(T[k]-T[k-1])/(OI[k]-OI[k-1])}
    if(OQ[k-1]<midi&&OQ[k]>=midi){EQ[++eq]=T[k-1]+(midi-OQ[k-1])*(T[k]-T[k-1])/(OQ[k]-OQ[k-1])}
  }
  per=(EI[ei]-EI[1])/(ei-1);
  dsum=0;dn=0; for(i=1;i<=ei;i++){for(j=1;j<=fi;j++){if(FI[j]>EI[i]){dsum+=FI[j]-EI[i];dn++;break}}}
  duty=dsum/dn/per*100;
  dq=EQ[1]-EI[1]; while(dq<0)dq+=per; while(dq>per)dq-=per; iq=dq/per*360;
  printf "%s: I_P %.0f / I_N %.0f / Q_P %.0f / Q_N %.0f mVpp | INVO3 %.0f..%.0f mV | f=%.3fGHz duty=%.1f%% I/Q=%.1fdeg\n",
    CORNER, (ipmx-ipmn)*1e3,(inmx-inmn)*1e3,(qpmx-qpmn)*1e3,(qnmx-qnmn)*1e3, oimn*1e3,oimx*1e3, 1e-9/per, duty, iq;
}
