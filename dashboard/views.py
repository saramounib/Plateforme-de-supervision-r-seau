from django.shortcuts import redirect, render#render:affiche page html#redirect:rediriger
from .models import Agence, Alerte
from django.db.models import Count, Avg, Max, Min, Sum
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.units import cm
from django.contrib.auth.decorators import login_required
# =====================================================
# TABLEAU DE BORD
# =====================================================
@login_required
def dashboard(request):
    detecter_anomalies()  # Appel de la fonction pour détecter les anomalies
    agences = Agence.objects.all()

    context = {#dictionnaire
        "total_agencies": Agence.objects.count(),

        "online_agencies": Agence.objects.filter(
            statut="En ligne"
        ).count(),

        "anomaly_agencies": Agence.objects.exclude(
            statut="En ligne"
        ).count(),

        "total_bandwidth": f"{round(Agence.objects.aggregate(total=Sum('bande_passante'))['total'] / 1000, 2)} Gbps",

        "availability": f"{round(Agence.objects.filter(statut='En ligne').count() / Agence.objects.count() * 100, 1) if Agence.objects.count() > 0 else 0} %",


        # =========================
        # TRAFIC
        # =========================

        "traffic_labels": [
            "00:00",
            "04:00",
            "08:00",
            "12:00",
            "16:00",
            "20:00",
            "24:00"
        ],

        "download_data": [
            420,
            350,
            510,
            430,
            760,
            540,
            580
        ],

        "upload_data": [
            220,
            190,
            270,
            240,
            390,
            260,
            300
        ],


        # =========================
        # AGENCES
        # =========================

        "agencies": agences,


        # =========================
        # ALERTES
        # =========================

        "alerts": Alerte.objects.select_related(
            "agence"
        ).all().order_by(
            "-date_creation"
        )[:5],

    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =====================================================
# AGENCES
# =====================================================

def agences(request):

    # Détection automatique des anomalies
    detecter_anomalies()

    agences = Agence.objects.all()

    total_agences = agences.count()

    agences_en_ligne = agences.filter(
        statut="En ligne"
    ).count()

    agences_anomalie = agences.filter(
        statut="Anomalie"
    ).count()

    if total_agences > 0:
        disponibilite = round(
            (agences_en_ligne / total_agences) * 100,
            1
        )
    else:
        disponibilite = 0

    return render(
        request,
        "agences.html",
        {
            "agences": agences,
            "total_agences": total_agences,
            "agences_en_ligne": agences_en_ligne,
            "agences_anomalie": agences_anomalie,
            "disponibilite": disponibilite,
        }
    )


# =====================================================
# CARTE RÉSEAU
# =====================================================

def carte_reseau(request):
    agences = Agence.objects.all()
    return render(
        request,
        "carte_reseau.html",
        {
            "agences": agences
        }
    )


# =====================================================
# PERFORMANCES
# =====================================================

def performances(request):
    agences = Agence.objects.all()
    return render(
        request,
        "performances.html",
        {
            "agences": agences
        }
    )


# =====================================================
# KPI
# =====================================================
def kpi(request):
    agences = Agence.objects.all()

    moyenne_latence = agences.aggregate(
        moyenne=Avg("latence")
    )["moyenne"] or 0

    moyenne_perte = agences.aggregate(
        moyenne=Avg("perte_paquets")
    )["moyenne"] or 0

    total_bande_passante = agences.aggregate(
        total=Sum("bande_passante")
    )["total"] or 0

    total_agences = agences.count()

    agences_en_ligne = agences.filter(
        statut="En ligne"
    ).count()

    agences_anomalie = agences.exclude(
        statut="En ligne"
    ).count()

    return render(
        request,
        "kpi.html",
        {
            "agences": agences,
            "total_agences": total_agences,
            "agences_en_ligne": agences_en_ligne,
            "agences_anomalie": agences_anomalie,
            "moyenne_latence": round(moyenne_latence, 2),
            "moyenne_perte": round(moyenne_perte, 2),
            "total_bande_passante": round(total_bande_passante, 2),
        }
    )

# =====================================================
# ALERTES
# =====================================================

def alertes(request):

    alertes = Alerte.objects.select_related(
        "agence"
    ).all().order_by(
        "-date_creation"
    )

    return render(
        request,
        "alertes.html",
        {
            "alertes": alertes
        }
    )

def resoudre_alerte(request, alerte_id):
    alerte = Alerte.objects.get(id=alerte_id)
    alerte.statut = "Résolue"
    alerte.save()
    return redirect("alertes")
# =====================================================
# HISTORIQUE
# =====================================================

def historique(request):
    alertes = Alerte.objects.select_related(
        "agence"
    ).all().order_by(
        "-date_creation"
    )
    return render(
        request,
        "historique.html",
        {
            "alertes": alertes
        }
    )


# =====================================================
# RAPPORTS
# =====================================================

def rapports(request):
    agences = Agence.objects.all()
    alertes = Alerte.objects.select_related(
        "agence"
    ).all().order_by(
        "-date_creation"
    )
    return render(
        request,
        "rapports.html",
        {
            "agences": agences,
            "alertes": alertes,
        }
    )


# =====================================================
# PROFIL
# =====================================================

def profil(request):

    return render(
        request,
        "profil.html"
    )
def detecter_anomalies():
    agences = Agence.objects.all()

    for agence in agences:

        # Une agence est en anomalie si :
        # Latence > 100 ms OU perte de paquets > 2 %
        anomalie = (
            agence.latence > 100
            or agence.perte_paquets > 2
        )

        if anomalie:

            # Mise à jour du statut
            agence.statut = "Anomalie"
            agence.save()

            # Alerte de latence
            if agence.latence > 100:

                alerte_existante = Alerte.objects.filter(
                    agence=agence,
                    type_alerte="Latence élevée",
                    statut="Ouverte"
                ).exists()

                if not alerte_existante:
                    Alerte.objects.create(
                        agence=agence,
                        type_alerte="Latence élevée",
                        severite="Haute",
                        statut="Ouverte"
                    )

            # Alerte de perte de paquets
            if agence.perte_paquets > 2:

                alerte_existante = Alerte.objects.filter(
                    agence=agence,
                    type_alerte="Perte de paquets",
                    statut="Ouverte"
                ).exists()

                if not alerte_existante:
                    Alerte.objects.create(
                        agence=agence,
                        type_alerte="Perte de paquets",
                        severite="Haute",
                        statut="Ouverte"
                    )

        else:
            # Si les paramètres sont normaux,
            # l'agence revient automatiquement en ligne
            agence.statut = "En ligne"
            agence.save()


def generer_rapport_pdf(request):

    agences = Agence.objects.all()
    alertes = Alerte.objects.select_related("agence").all().order_by("-date_creation")

    # Création de la réponse HTTP
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="rapport_sdwan.pdf"'

    # Création du document PDF
    document = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()

    titre_style = ParagraphStyle(
        "Titre",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=20
    )

    sous_titre_style = ParagraphStyle(
        "SousTitre",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=20
    )

    elements = []

    # =========================
    # TITRE
    # =========================

    elements.append(
        Paragraph(
            "Rapport de supervision du réseau SD-WAN",
            titre_style
        )
    )

    elements.append(
        Paragraph(
            "Plateforme de supervision et de détection d'anomalies",
            sous_titre_style
        )
    )

    elements.append(Spacer(1, 10))

    # =========================
    # RÉSUMÉ
    # =========================

    total_agences = agences.count()
    agences_en_ligne = agences.filter(statut="En ligne").count()
    agences_anomalie = agences.exclude(statut="En ligne").count()
    total_alertes = alertes.count()

    resume_data = [
        ["Indicateur", "Valeur"],
        ["Nombre total d'agences", str(total_agences)],
        ["Agences en ligne", str(agences_en_ligne)],
        ["Agences en anomalie", str(agences_anomalie)],
        ["Nombre total d'alertes", str(total_alertes)],
    ]

    resume_table = Table(
        resume_data,
        colWidths=[10 * cm, 6 * cm]
    )

    resume_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ])
    )

    elements.append(
        Paragraph(
            "1. Résumé du réseau",
            styles["Heading2"]
        )
    )

    elements.append(resume_table)
    elements.append(Spacer(1, 20))

    # =========================
    # PERFORMANCES DES AGENCES
    # =========================

    elements.append(
        Paragraph(
            "2. Performances des agences",
            styles["Heading2"]
        )
    )

    agences_data = [
        [
            "Agence",
            "Ville",
            "Latence",
            "Perte",
            "Bande passante",
            "Statut"
        ]
    ]

    for agence in agences:

        agences_data.append([
            agence.nom,
            agence.ville,
            f"{agence.latence} ms",
            f"{agence.perte_paquets} %",
            f"{agence.bande_passante} Mbps",
            agence.statut
        ])

    agences_table = Table(
        agences_data,
        repeatRows=1,
        colWidths=[
            3 * cm,
            3 * cm,
            2.3 * cm,
            2.3 * cm,
            3 * cm,
            2.5 * cm
        ]
    )

    agences_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(agences_table)
    elements.append(Spacer(1, 20))

    # =========================
    # ALERTES
    # =========================

    elements.append(
        Paragraph(
            "3. Historique des alertes",
            styles["Heading2"]
        )
    )

    alertes_data = [
        [
            "Agence",
            "Type",
            "Sévérité",
            "Statut",
            "Date"
        ]
    ]

    for alerte in alertes:

        alertes_data.append([
            alerte.agence.nom,
            alerte.type_alerte,
            alerte.severite,
            alerte.statut,
            alerte.date_creation.strftime("%d/%m/%Y %H:%M")
        ])

    if len(alertes_data) == 1:

        alertes_data.append([
            "Aucune",
            "Aucune alerte",
            "-",
            "-",
            "-"
        ])

    alertes_table = Table(
        alertes_data,
        repeatRows=1,
        colWidths=[
            3.5 * cm,
            4 * cm,
            2.5 * cm,
            2.5 * cm,
            4 * cm
        ]
    )

    alertes_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (2, 1), (3, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(alertes_table)
    elements.append(Spacer(1, 20))

    # =========================
    # CONCLUSION
    # =========================

    elements.append(
        Paragraph(
            "4. Conclusion",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            "Ce rapport présente l'état actuel des agences supervisées "
            "ainsi que les performances et les alertes détectées par la "
            "plateforme de supervision SD-WAN.",
            styles["Normal"]
        )
    )

    # Génération du PDF
    document.build(elements)

    return response